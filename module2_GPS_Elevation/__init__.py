"""
GPS高程拟合模块
提供平面拟合、二次曲面拟合、四参数拟合三种模型
支持自动模型选择和精度评估
"""

from .elevation_fitter import ElevationFitter, FittingResult
from .models import FittingModel, PlaneModel, QuadraticModel, FourParamModel, get_model, get_all_models

__all__ = [
    'ElevationFitter',
    'FittingResult',
    'FittingModel',
    'PlaneModel',
    'QuadraticModel',
    'FourParamModel',
    'get_model',
    'get_all_models'
]
