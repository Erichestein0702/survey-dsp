"""
GPS时间计算模块
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class GPSTimeData:
    """GPS时间数据"""
    week: int
    seconds: float
    
    @property
    def day_of_week(self) -> int:
        """周内第几天 (0=周日, 1=周一, ...)"""
        return int(self.seconds // 86400)
    
    @property
    def time_of_day(self) -> Tuple[int, int, float]:
        """当天的时间 (时, 分, 秒)"""
        remaining = self.seconds % 86400
        hours = int(remaining // 3600)
        remaining %= 3600
        minutes = int(remaining // 60)
        seconds = remaining % 60
        return (hours, minutes, seconds)
    
    def __str__(self) -> str:
        h, m, s = self.time_of_day
        return f"Week {self.week}, Day {self.day_of_week}, {h:02d}:{m:02d}:{s:06.3f}"


class GPSTimeCalculator:
    """GPS时间计算器"""
    
    GPS_EPOCH_JD = 2444244.5
    SECONDS_PER_WEEK = 604800
    SECONDS_PER_DAY = 86400
    
    @staticmethod
    def jd_to_gps(jd: float) -> GPSTimeData:
        """
        儒略日转GPS时间
        
        Args:
            jd: 儒略日
            
        Returns:
            GPSTimeData对象
        """
        days_since_epoch = jd - GPSTimeCalculator.GPS_EPOCH_JD
        
        total_seconds = days_since_epoch * GPSTimeCalculator.SECONDS_PER_DAY
        week = int(total_seconds // GPSTimeCalculator.SECONDS_PER_WEEK)
        seconds = total_seconds % GPSTimeCalculator.SECONDS_PER_WEEK
        
        return GPSTimeData(week=week, seconds=seconds)
    
    @staticmethod
    def gps_to_jd(week: int, seconds: float) -> float:
        """
        GPS时间转儒略日
        
        Args:
            week: GPS周
            seconds: 周内秒
            
        Returns:
            儒略日
        """
        total_seconds = week * GPSTimeCalculator.SECONDS_PER_WEEK + seconds
        days = total_seconds / GPSTimeCalculator.SECONDS_PER_DAY
        return GPSTimeCalculator.GPS_EPOCH_JD + days
    
    @staticmethod
    def gregorian_to_gps(year: int, month: int, day: int, 
                         hour: int = 0, minute: int = 0, second: float = 0.0) -> GPSTimeData:
        """
        公历转GPS时间
        
        Args:
            year: 年
            month: 月
            day: 日
            hour: 时
            minute: 分
            second: 秒
            
        Returns:
            GPSTimeData对象
        """
        from .julian_day import JulianDay
        jd = JulianDay.gregorian_to_jd(year, month, day, hour, minute, second)
        return GPSTimeCalculator.jd_to_gps(jd)
    
    @staticmethod
    def validate_gps_time(week: int, seconds: float) -> bool:
        """
        验证GPS时间是否有效
        
        Args:
            week: GPS周
            seconds: 周内秒
            
        Returns:
            是否有效
        """
        if week < 0:
            return False
        if seconds < 0 or seconds >= GPSTimeCalculator.SECONDS_PER_WEEK:
            return False
        return True
