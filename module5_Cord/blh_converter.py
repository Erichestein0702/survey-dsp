"""
大地坐标转换模块
实现空间直角坐标(XYZ)与大地坐标(BLH)之间的转换
"""

import numpy as np
import math
from typing import Tuple
from dataclasses import dataclass

from common.logger import get_logger
from common.ellipsoid_manager import Ellipsoid

logger = get_logger("BLHConverter")


@dataclass
class BLHCoordinate:
    """大地坐标数据类"""
    B: float  # 纬度（弧度）
    L: float  # 经度（弧度）
    H: float  # 大地高（米）
    
    @property
    def B_deg(self) -> float:
        """纬度（度）"""
        return math.degrees(self.B)
    
    @property
    def L_deg(self) -> float:
        """经度（度）"""
        return math.degrees(self.L)
    
    def __repr__(self):
        return f"BLH(B={self.B_deg:.6f}°, L={self.L_deg:.6f}°, H={self.H:.3f}m)"


class BLHConverter:
    """
    大地坐标转换器
    实现XYZ与BLH之间的相互转换
    """
    
    # 迭代收敛阈值
    ITERATION_THRESHOLD = 1e-10
    MAX_ITERATIONS = 100
    
    def __init__(self, ellipsoid: Ellipsoid):
        """
        初始化转换器
        
        Args:
            ellipsoid: 椭球参数
        """
        self.ellipsoid = ellipsoid
        logger.info(f"BLH转换器初始化完成，使用椭球: {ellipsoid.name}")
    
    def xyz_to_blh(self, X: float, Y: float, Z: float) -> BLHCoordinate:
        """
        空间直角坐标转大地坐标
        
        Args:
            X: X坐标（米）
            Y: Y坐标（米）
            Z: Z坐标（米）
            
        Returns:
            BLHCoordinate: 大地坐标
        """
        logger.log_algorithm_start("XYZ转BLH", {'X': X, 'Y': Y, 'Z': Z})
        
        a = self.ellipsoid.a
        b = self.ellipsoid.b
        e2 = self.ellipsoid.e2
        e2_prime = self.ellipsoid.e2_prime
        
        # 计算经度L（直接求解）
        L = math.atan2(Y, X)
        
        # 计算p（辅助变量）
        p = math.sqrt(X**2 + Y**2)
        
        # 迭代计算纬度B
        # 初始值
        theta = math.atan2(Z * a, p * b)
        B = math.atan2(Z + e2_prime * b * math.sin(theta)**3,
                      p - e2 * a * math.cos(theta)**3)
        
        iteration = 0
        B_prev = 0.0
        
        while abs(B - B_prev) > self.ITERATION_THRESHOLD and iteration < self.MAX_ITERATIONS:
            B_prev = B
            theta = math.atan2(Z + e2_prime * b * math.sin(B)**3,
                              p - e2 * a * math.cos(B)**3)
            B = theta
            iteration += 1
            
            logger.log_iteration("XYZ转BLH", iteration, abs(B - B_prev), self.ITERATION_THRESHOLD)
        
        # 计算卯酉圈曲率半径N
        N = a / math.sqrt(1 - e2 * math.sin(B)**2)
        
        # 计算大地高H
        H = p / math.cos(B) - N
        
        logger.log_algorithm_end("XYZ转BLH", f"迭代{iteration}次收敛")
        
        return BLHCoordinate(B, L, H)
    
    def blh_to_xyz(self, B: float, L: float, H: float) -> Tuple[float, float, float]:
        """
        大地坐标转空间直角坐标
        
        Args:
            B: 纬度（弧度）
            L: 经度（弧度）
            H: 大地高（米）
            
        Returns:
            (X, Y, Z): 空间直角坐标
        """
        logger.log_algorithm_start("BLH转XYZ", {'B': B, 'L': L, 'H': H})
        
        a = self.ellipsoid.a
        e2 = self.ellipsoid.e2
        
        # 计算卯酉圈曲率半径N
        N = a / math.sqrt(1 - e2 * math.sin(B)**2)
        
        # 计算XYZ
        X = (N + H) * math.cos(B) * math.cos(L)
        Y = (N + H) * math.cos(B) * math.sin(L)
        Z = (N * (1 - e2) + H) * math.sin(B)
        
        logger.log_algorithm_end("BLH转XYZ", f"N={N:.3f}")
        
        return (X, Y, Z)
    
    def batch_xyz_to_blh(self, coords: np.ndarray) -> np.ndarray:
        """
        批量XYZ转BLH
        
        Args:
            coords: Nx3数组，每行是[X, Y, Z]
            
        Returns:
            Nx3数组，每行是[B, L, H]（弧度）
        """
        results = []
        for coord in coords:
            blh = self.xyz_to_blh(coord[0], coord[1], coord[2])
            results.append([blh.B, blh.L, blh.H])
        return np.array(results)
    
    def batch_blh_to_xyz(self, coords: np.ndarray) -> np.ndarray:
        """
        批量BLH转XYZ
        
        Args:
            coords: Nx3数组，每行是[B, L, H]（弧度）
            
        Returns:
            Nx3数组，每行是[X, Y, Z]
        """
        results = []
        for coord in coords:
            xyz = self.blh_to_xyz(coord[0], coord[1], coord[2])
            results.append(xyz)
        return np.array(results)
