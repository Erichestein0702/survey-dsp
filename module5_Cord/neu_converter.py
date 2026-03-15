"""
站心坐标转换模块
实现空间直角坐标(XYZ)与站心坐标(NEU)之间的转换
"""

import numpy as np
import math
from typing import Tuple
from dataclasses import dataclass

from common.logger import get_logger
from common.ellipsoid_manager import Ellipsoid
from .blh_converter import BLHConverter

logger = get_logger("NEUConverter")


@dataclass
class NEUCoordinate:
    """站心坐标数据类"""
    N: float  # 北向分量（米）
    E: float  # 东向分量（米）
    U: float  # 天向分量（米）
    
    def __repr__(self):
        return f"NEU(N={self.N:.6f}m, E={self.E:.6f}m, U={self.U:.6f}m)"


class NEUConverter:
    """
    站心坐标转换器
    实现XYZ与NEU之间的转换
    """
    
    def __init__(self, ellipsoid: Ellipsoid):
        """
        初始化转换器
        
        Args:
            ellipsoid: 椭球参数
        """
        self.ellipsoid = ellipsoid
        self.blh_converter = BLHConverter(ellipsoid)
        logger.info(f"NEU转换器初始化完成，使用椭球: {ellipsoid.name}")
    
    def xyz_to_neu(self, X: float, Y: float, Z: float,
                   X0: float, Y0: float, Z0: float) -> NEUCoordinate:
        """
        空间直角坐标转站心坐标
        
        Args:
            X, Y, Z: 待转换点的空间直角坐标
            X0, Y0, Z0: 基准点的空间直角坐标
            
        Returns:
            NEUCoordinate: 站心坐标
        """
        logger.log_algorithm_start("XYZ转NEU", {
            '点': (X, Y, Z), '基准点': (X0, Y0, Z0)
        })
        
        # 基准点转大地坐标
        blh0 = self.blh_converter.xyz_to_blh(X0, Y0, Z0)
        B0, L0 = blh0.B, blh0.L
        
        # 构建旋转矩阵
        sinB, cosB = math.sin(B0), math.cos(B0)
        sinL, cosL = math.sin(L0), math.cos(L0)
        
        # 旋转矩阵 T
        T = np.array([
            [-sinB * cosL, -sinB * sinL, cosB],
            [-sinL, cosL, 0],
            [cosB * cosL, cosB * sinL, sinB]
        ])
        
        # 坐标差
        dX = np.array([X - X0, Y - Y0, Z - Z0])
        
        # 站心坐标
        neu = T @ dX
        
        logger.log_algorithm_end("XYZ转NEU", f"N={neu[0]:.3f}, E={neu[1]:.3f}, U={neu[2]:.3f}")
        
        return NEUCoordinate(neu[0], neu[1], neu[2])
    
    def neu_to_xyz(self, N: float, E: float, U: float,
                   X0: float, Y0: float, Z0: float) -> Tuple[float, float, float]:
        """
        站心坐标转空间直角坐标
        
        Args:
            N, E, U: 站心坐标
            X0, Y0, Z0: 基准点的空间直角坐标
            
        Returns:
            (X, Y, Z): 空间直角坐标
        """
        logger.log_algorithm_start("NEU转XYZ", {
            'NEU': (N, E, U), '基准点': (X0, Y0, Z0)
        })
        
        # 基准点转大地坐标
        blh0 = self.blh_converter.xyz_to_blh(X0, Y0, Z0)
        B0, L0 = blh0.B, blh0.L
        
        # 构建旋转矩阵的转置（逆矩阵）
        sinB, cosB = math.sin(B0), math.cos(B0)
        sinL, cosL = math.sin(L0), math.cos(L0)
        
        # 旋转矩阵 T 是正交矩阵，T^{-1} = T^T
        T_inv = np.array([
            [-sinB * cosL, -sinL, cosB * cosL],
            [-sinB * sinL, cosL, cosB * sinL],
            [cosB, 0, sinB]
        ])
        
        # 站心坐标
        neu = np.array([N, E, U])
        
        # 坐标差
        dX = T_inv @ neu
        
        # 目标点坐标
        X = X0 + dX[0]
        Y = Y0 + dX[1]
        Z = Z0 + dX[2]
        
        logger.log_algorithm_end("NEU转XYZ", f"X={X:.3f}, Y={Y:.3f}, Z={Z:.3f}")
        
        return (X, Y, Z)
