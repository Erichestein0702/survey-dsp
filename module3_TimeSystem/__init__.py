"""
时间系统转换模块
"""

from .time_converter import TimeConverter
from .julian_day import JulianDay
from .gps_time import GPSTimeCalculator, GPSTimeData
from .models import TimeType, GregorianTime, GPSTime, TimeConversionResult
from .file_processor import TimeFileProcessor, TimeDataRecord, BatchConversionResult

__all__ = [
    'TimeConverter',
    'JulianDay',
    'GPSTimeCalculator',
    'GPSTimeData',
    'TimeType',
    'GregorianTime',
    'GPSTime',
    'TimeConversionResult',
    'TimeFileProcessor',
    'TimeDataRecord',
    'BatchConversionResult'
]

__version__ = '1.0.0'

GPS_EPOCH_JD = 2444244.5

def gregorian_to_jd(year, month, day, hour=0, minute=0, second=0.0):
    """公历转儒略日快捷函数"""
    return JulianDay.gregorian_to_jd(year, month, day, hour, minute, second)

def jd_to_gregorian(jd):
    """儒略日转公历快捷函数"""
    return JulianDay.jd_to_gregorian(jd)

def jd_to_gps(jd):
    """儒略日转GPS时间快捷函数"""
    return GPSTimeCalculator.jd_to_gps(jd)

def gps_to_jd(week, seconds):
    """GPS时间转儒略日快捷函数"""
    return GPSTimeCalculator.gps_to_jd(week, seconds)

def full_conversion(**kwargs):
    """完整时间转换快捷函数"""
    return TimeConverter.full_conversion(**kwargs)

__all__.extend([
    'gregorian_to_jd',
    'jd_to_gregorian',
    'jd_to_gps',
    'gps_to_jd',
    'full_conversion',
    'GPS_EPOCH_JD'
])
