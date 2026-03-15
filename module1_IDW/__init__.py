"""
IDW插值模块
"""

from .idw_interpolator import IDWInterpolator
from .models import KnownPoint, TargetPoint, IDWResult, IDWBatchResult

__all__ = [
    'IDWInterpolator',
    'KnownPoint',
    'TargetPoint',
    'IDWResult',
    'IDWBatchResult'
]

__version__ = '1.0.0'

DEFAULT_POWER = 2.0
DEFAULT_SEARCH_RADIUS = None

def interpolate(known_points, target_points, power=2.0, search_radius=None):
    """IDW插值快捷函数"""
    interpolator = IDWInterpolator(known_points, power, search_radius)
    return interpolator.interpolate_batch(target_points)

__all__.extend([
    'interpolate',
    'DEFAULT_POWER',
    'DEFAULT_SEARCH_RADIUS'
])
