"""
滑坡监测模块
提供位移速度、相对应变计算和预警功能
"""

from .deformation_analyzer import DeformationAnalyzer, DeformationResult
from .strain_calculator import StrainCalculator, StrainResult, MonitoringPoint, PointPair

__all__ = [
    'DeformationAnalyzer',
    'DeformationResult',
    'StrainCalculator',
    'StrainResult',
    'MonitoringPoint',
    'PointPair'
]

__version__ = '1.0.0'
