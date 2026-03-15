"""
时间系统转换核心模块
"""

from typing import Union, Tuple, Optional
from .julian_day import JulianDay
from .gps_time import GPSTimeCalculator, GPSTimeData
from .models import TimeType, GregorianTime, GPSTime, TimeConversionResult


class TimeConverter:
    """时间系统转换器"""
    
    @staticmethod
    def convert_gregorian_to_jd(year: int, month: int, day: int,
                                 hour: int = 0, minute: int = 0, second: float = 0.0) -> TimeConversionResult:
        """
        公历转儒略日
        
        Args:
            year: 年
            month: 月
            day: 日
            hour: 时 (0-23)
            minute: 分 (0-59)
            second: 秒 (0-60)
            
        Returns:
            TimeConversionResult
        """
        jd = JulianDay.gregorian_to_jd(year, month, day, hour, minute, second)
        
        return TimeConversionResult(
            input_type=TimeType.GREGORIAN,
            output_type=TimeType.JULIAN_DAY,
            gregorian=GregorianTime(year, month, day, hour, minute, second),
            julian_day=jd
        )
    
    @staticmethod
    def convert_jd_to_gregorian(jd: float) -> TimeConversionResult:
        """
        儒略日转公历
        
        Args:
            jd: 儒略日
            
        Returns:
            TimeConversionResult
        """
        year, month, day, hour, minute, second = JulianDay.jd_to_gregorian(jd)
        
        return TimeConversionResult(
            input_type=TimeType.JULIAN_DAY,
            output_type=TimeType.GREGORIAN,
            gregorian=GregorianTime(year, month, day, hour, minute, second),
            julian_day=jd
        )
    
    @staticmethod
    def convert_jd_to_gps(jd: float) -> TimeConversionResult:
        """
        儒略日转GPS时间
        
        Args:
            jd: 儒略日
            
        Returns:
            TimeConversionResult
        """
        gps_data = GPSTimeCalculator.jd_to_gps(jd)
        
        return TimeConversionResult(
            input_type=TimeType.JULIAN_DAY,
            output_type=TimeType.GPS_TIME,
            julian_day=jd,
            gps_time=GPSTime(gps_data.week, gps_data.seconds)
        )
    
    @staticmethod
    def convert_gps_to_jd(week: int, seconds: float) -> TimeConversionResult:
        """
        GPS时间转儒略日
        
        Args:
            week: GPS周
            seconds: 周内秒
            
        Returns:
            TimeConversionResult
        """
        jd = GPSTimeCalculator.gps_to_jd(week, seconds)
        
        return TimeConversionResult(
            input_type=TimeType.GPS_TIME,
            output_type=TimeType.JULIAN_DAY,
            julian_day=jd,
            gps_time=GPSTime(week, seconds)
        )
    
    @staticmethod
    def convert_gregorian_to_gps(year: int, month: int, day: int,
                                  hour: int = 0, minute: int = 0, second: float = 0.0) -> TimeConversionResult:
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
            TimeConversionResult
        """
        gps_data = GPSTimeCalculator.gregorian_to_gps(year, month, day, hour, minute, second)
        
        return TimeConversionResult(
            input_type=TimeType.GREGORIAN,
            output_type=TimeType.GPS_TIME,
            gregorian=GregorianTime(year, month, day, hour, minute, second),
            gps_time=GPSTime(gps_data.week, gps_data.seconds)
        )
    
    @staticmethod
    def convert_gps_to_gregorian(week: int, seconds: float) -> TimeConversionResult:
        """
        GPS时间转公历
        
        Args:
            week: GPS周
            seconds: 周内秒
            
        Returns:
            TimeConversionResult
        """
        jd = GPSTimeCalculator.gps_to_jd(week, seconds)
        year, month, day, hour, minute, second = JulianDay.jd_to_gregorian(jd)
        
        return TimeConversionResult(
            input_type=TimeType.GPS_TIME,
            output_type=TimeType.GREGORIAN,
            gregorian=GregorianTime(year, month, day, hour, minute, second),
            julian_day=jd,
            gps_time=GPSTime(week, seconds)
        )
    
    @staticmethod
    def full_conversion(year: int = None, month: int = None, day: int = None,
                        hour: int = 0, minute: int = 0, second: float = 0.0,
                        jd: float = None, week: int = None, seconds: float = None) -> dict:
        """
        完整时间转换 - 输入任意一种时间格式，输出所有格式
        
        Args:
            year, month, day, hour, minute, second: 公历时间
            jd: 儒略日
            week, seconds: GPS时间
            
        Returns:
            包含所有时间格式的字典
        """
        if jd is not None:
            year, month, day, hour, minute, second = JulianDay.jd_to_gregorian(jd)
            gps_data = GPSTimeCalculator.jd_to_gps(jd)
            week, seconds = gps_data.week, gps_data.seconds
        elif week is not None and seconds is not None:
            jd = GPSTimeCalculator.gps_to_jd(week, seconds)
            year, month, day, hour, minute, second = JulianDay.jd_to_gregorian(jd)
        elif year is not None:
            jd = JulianDay.gregorian_to_jd(year, month, day, hour, minute, second)
            gps_data = GPSTimeCalculator.jd_to_gps(jd)
            week, seconds = gps_data.week, gps_data.seconds
        else:
            raise ValueError("必须提供至少一种时间格式")
        
        return {
            'gregorian': GregorianTime(year, month, day, hour, minute, second),
            'julian_day': jd,
            'gps_time': GPSTime(week, seconds)
        }
    
    @staticmethod
    def full_workflow(year: int = None, month: int = None, day: int = None,
                      hour: int = 0, minute: int = 0, second: float = 0.0,
                      jd: float = None) -> dict:
        """
        完整工作流 - 输出题目要求的完整格式
        
        Args:
            year, month, day, hour, minute, second: 公历时间
            jd: 儒略日
            
        Returns:
            包含所有结果的字典
        """
        if jd is not None:
            year, month, day, hour, minute, second = JulianDay.jd_to_gregorian(jd)
        else:
            jd = JulianDay.gregorian_to_jd(year, month, day, hour, minute, second)
        
        day_of_year = JulianDay.day_of_year(year, month, day)
        fishing_status = JulianDay.fishing_net_status(year, month, day)
        
        gps_data = GPSTimeCalculator.jd_to_gps(jd)
        
        return {
            'gregorian': GregorianTime(year, month, day, hour, minute, second),
            'julian_day': jd,
            'gps_time': GPSTime(gps_data.week, gps_data.seconds),
            'day_of_year': day_of_year,
            'fishing_status': fishing_status
        }
    
    @staticmethod
    def format_output(results: list) -> str:
        """
        格式化输出为题目要求的形式
        
        Args:
            results: full_workflow结果列表
            
        Returns:
            格式化字符串
        """
        lines = []
        
        lines.append("-------JD-----------")
        for r in results:
            lines.append(f"{r['julian_day']:.6f}")
        
        lines.append("")
        lines.append("-------公历（年 月 日 时：分：秒）----------")
        for r in results:
            g = r['gregorian']
            lines.append(f"{g.year} {g.month} {g.day} {g.hour} {g.minute} {int(g.second)}")
        
        lines.append("")
        lines.append("-------年积日----------")
        for r in results:
            lines.append(f"第{r['day_of_year']}日")
        
        lines.append("")
        lines.append("-------三天打鱼两天晒网----------")
        for r in results:
            lines.append(r['fishing_status'])
        
        return "\n".join(lines)
