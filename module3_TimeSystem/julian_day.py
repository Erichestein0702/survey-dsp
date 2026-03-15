"""
儒略日计算模块
"""

import math
from typing import Tuple


class JulianDay:
    """儒略日计算器"""
    
    GPS_EPOCH_JD = 2444244.5  # GPS起点: 1980-01-06 00:00:00 UT
    
    @staticmethod
    def gregorian_to_jd(year: int, month: int, day: int, 
                        hour: int = 0, minute: int = 0, second: float = 0.0) -> float:
        """
        公历转儒略日
        
        Args:
            year: 年
            month: 月
            day: 日
            hour: 时
            minute: 分
            second: 秒
            
        Returns:
            儒略日
        """
        if month <= 2:
            year -= 1
            month += 12
        
        A = int(year / 100)
        B = 2 - A + int(A / 4)
        
        UT = hour + minute / 60.0 + second / 3600.0
        
        JD = (int(365.25 * (year + 4716)) + 
              int(30.6001 * (month + 1)) + 
              day + B - 1524.5 + UT / 24.0)
        
        return JD
    
    @staticmethod
    def jd_to_gregorian(jd: float) -> Tuple[int, int, int, int, int, float]:
        """
        儒略日转公历
        
        Args:
            jd: 儒略日
            
        Returns:
            (year, month, day, hour, minute, second)
        """
        jd = jd + 0.5
        Z = int(jd)
        F = jd - Z
        
        if Z < 2299161:
            A = Z
        else:
            alpha = int((Z - 1867216.25) / 36524.25)
            A = Z + 1 + alpha - int(alpha / 4)
        
        B = A + 1524
        C = int((B - 122.1) / 365.25)
        D = int(365.25 * C)
        E = int((B - D) / 30.6001)
        
        day = B - D - int(30.6001 * E)
        
        if E < 14:
            month = E - 1
        else:
            month = E - 13
        
        if month > 2:
            year = C - 4716
        else:
            year = C - 4715
        
        hours = F * 24.0
        hour = int(hours)
        
        minutes = (hours - hour) * 60.0
        minute = int(minutes)
        
        second = (minutes - minute) * 60.0
        
        return (year, month, day, hour, minute, second)
    
    @staticmethod
    def jd_to_gps(jd: float) -> Tuple[int, float]:
        """
        儒略日转GPS时间
        
        Args:
            jd: 儒略日
            
        Returns:
            (week, seconds) GPS周和周内秒
        """
        days_since_gps_epoch = jd - JulianDay.GPS_EPOCH_JD
        
        week = int(days_since_gps_epoch / 7)
        seconds = (days_since_gps_epoch - week * 7) * 86400.0
        
        return (week, seconds)
    
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
        jd = JulianDay.GPS_EPOCH_JD + week * 7 + seconds / 86400.0
        return jd
    
    @staticmethod
    def is_leap_year(year: int) -> bool:
        """判断是否为闰年"""
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    
    @staticmethod
    def days_in_month(year: int, month: int) -> int:
        """获取某月的天数"""
        days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if month == 2 and JulianDay.is_leap_year(year):
            return 29
        return days[month]
    
    @staticmethod
    def day_of_year(year: int, month: int, day: int) -> int:
        """
        计算年积日（一年中的第几天）
        1月1日为第1日
        
        Args:
            year: 年
            month: 月
            day: 日
            
        Returns:
            年积日
        """
        doy = 0
        for m in range(1, month):
            doy += JulianDay.days_in_month(year, m)
        doy += day
        return doy
    
    @staticmethod
    def fishing_net_status(year: int, month: int, day: int) -> str:
        """
        计算"三天打鱼两天晒网"状态
        从2016年1月1日开始，3天打鱼2天晒网循环
        
        Args:
            year: 年
            month: 月
            day: 日
            
        Returns:
            "打鱼" 或 "晒网"
        """
        start_year, start_month, start_day = 2016, 1, 1
        start_doy = 1
        
        current_doy = JulianDay.day_of_year(year, month, day)
        
        year_diff = year - start_year
        total_days = 0
        for y in range(start_year, year):
            total_days += 366 if JulianDay.is_leap_year(y) else 365
        
        total_days += current_doy - start_doy
        
        cycle = 5
        position = total_days % cycle
        
        if position < 3:
            return "打鱼"
        else:
            return "晒网"
