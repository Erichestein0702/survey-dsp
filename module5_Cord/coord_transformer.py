"""
坐标转换核心模块
整合BLH和NEU转换功能
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from dataclasses import dataclass

from common.logger import get_logger
from common.parser import DataParser, ParseResult
from common.exporter import Exporter
from common.ellipsoid_manager import EllipsoidManager, Ellipsoid
from .blh_converter import BLHConverter, BLHCoordinate
from .neu_converter import NEUConverter, NEUCoordinate

logger = get_logger("CoordinateTransformer")


@dataclass
class TransformResult:
    """坐标转换结果"""
    original_coords: List[Tuple[float, float, float]]
    converted_coords: List
    ellipsoid_name: str
    conversion_type: str


class CoordinateTransformer:
    """坐标转换器"""
    
    def __init__(self, ellipsoid_name: str = "WGS84"):
        """初始化转换器"""
        self.ellipsoid_manager = EllipsoidManager()
        self.ellipsoid = self.ellipsoid_manager.get_ellipsoid(ellipsoid_name)
        self.blh_converter = BLHConverter(self.ellipsoid)
        self.neu_converter = NEUConverter(self.ellipsoid)
        self.parser = DataParser()
        self.exporter = Exporter()
        logger.info(f"坐标转换器初始化完成，使用椭球: {ellipsoid_name}")
    
    def xyz_to_blh_batch(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray) -> List[BLHCoordinate]:
        """批量XYZ转BLH"""
        results = []
        for x, y, z in zip(X, Y, Z):
            results.append(self.blh_converter.xyz_to_blh(x, y, z))
        return results
    
    def blh_to_xyz_batch(self, B: np.ndarray, L: np.ndarray, H: np.ndarray) -> List[Tuple]:
        """批量BLH转XYZ"""
        results = []
        for b, l, h in zip(B, L, H):
            results.append(self.blh_converter.blh_to_xyz(b, l, h))
        return results
    
    def xyz_to_neu_batch(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                        X0: float, Y0: float, Z0: float) -> List[NEUCoordinate]:
        """批量XYZ转NEU"""
        results = []
        for x, y, z in zip(X, Y, Z):
            results.append(self.neu_converter.xyz_to_neu(x, y, z, X0, Y0, Z0))
        return results
    
    def load_coordinates(self, file_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """从文件加载坐标"""
        parse_result = self.parser.parse_coordinates(file_path)
        X = parse_result.data['X'].values
        Y = parse_result.data['Y'].values
        Z = parse_result.data['Z'].values
        logger.info(f"加载了 {len(X)} 个坐标点")
        return X, Y, Z
    
    def generate_report(self, result: TransformResult, title: str = "坐标转换报告") -> str:
        """生成报告"""
        report = self.exporter.create_report_header(title, "模块5 - 坐标转换")
        report += f"**椭球**: {result.ellipsoid_name}\n"
        report += f"**转换类型**: {result.conversion_type}\n\n"
        return report
