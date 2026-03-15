"""
多边形面积计算模块
提供格雷厄姆扫描、鞋带公式、三角剖分、海伦公式等算法
支持凹多边形计算和双重校验
"""

from .area_calculator import AreaCalculator, AreaResult
from .graham_scan import GrahamScan
from .heron_calculator import HeronCalculator, HeronTriangle, HeronAreaResult

__all__ = [
    'AreaCalculator',
    'AreaResult',
    'GrahamScan',
    'HeronCalculator',
    'HeronTriangle',
    'HeronAreaResult'
]
