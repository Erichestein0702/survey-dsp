"""
度分秒(DMS)格式转换模块
实现十进制度数与度分秒格式之间的转换
"""

import math
from typing import Tuple
from dataclasses import dataclass


@dataclass
class DMS:
    """度分秒数据类"""
    degrees: int      # 度
    minutes: int      # 分
    seconds: float    # 秒
    sign: int         # 符号 (1或-1)
    
    def __str__(self) -> str:
        """格式化为字符串"""
        sign_char = "-" if self.sign < 0 else ""
        return f"{sign_char}{abs(self.degrees)}°{self.minutes:02d}'{self.seconds:06.3f}\""
    
    def to_decimal(self) -> float:
        """转换为十进制度数"""
        decimal = self.degrees + self.minutes / 60.0 + self.seconds / 3600.0
        return self.sign * decimal


class DMSConverter:
    """度分秒转换器"""
    
    @staticmethod
    def decimal_to_dms(decimal_degrees: float) -> DMS:
        """
        十进制度数转度分秒
        
        Args:
            decimal_degrees: 十进制度数
            
        Returns:
            DMS: 度分秒对象
        """
        # 保存符号
        sign = 1 if decimal_degrees >= 0 else -1
        decimal_degrees = abs(decimal_degrees)
        
        # 提取度
        degrees = int(decimal_degrees)
        
        # 提取分
        remaining = (decimal_degrees - degrees) * 60
        minutes = int(remaining)
        
        # 提取秒
        seconds = (remaining - minutes) * 60
        
        # 处理秒数进位
        if seconds >= 60:
            seconds -= 60
            minutes += 1
        
        if minutes >= 60:
            minutes -= 60
            degrees += 1
        
        return DMS(degrees, minutes, seconds, sign)
    
    @staticmethod
    def dms_to_decimal(degrees: int, minutes: int, seconds: float, sign: int = 1) -> float:
        """
        度分秒转十进制度数
        
        Args:
            degrees: 度
            minutes: 分
            seconds: 秒
            sign: 符号 (1或-1)
            
        Returns:
            float: 十进制度数
        """
        dms = DMS(degrees, minutes, seconds, sign)
        return dms.to_decimal()
    
    @staticmethod
    def format_blh_dms(B_deg: float, L_deg: float, H: float) -> str:
        """
        格式化大地坐标为度分秒格式
        
        Args:
            B_deg: 纬度（十进制度数）
            L_deg: 经度（十进制度数）
            H: 大地高（米）
            
        Returns:
            str: 格式化字符串
        """
        B_dms = DMSConverter.decimal_to_dms(B_deg)
        L_dms = DMSConverter.decimal_to_dms(L_deg)
        
        # 确定经纬度方向
        B_dir = "N" if B_dms.sign >= 0 else "S"
        L_dir = "E" if L_dms.sign >= 0 else "W"
        
        return (
            f"B = {abs(B_dms.degrees)}°{B_dms.minutes:02d}'{B_dms.seconds:06.3f}\"{B_dir}, "
            f"L = {abs(L_dms.degrees)}°{L_dms.minutes:02d}'{L_dms.seconds:06.3f}\"{L_dir}, "
            f"H = {H:.3f}m"
        )
    
    @staticmethod
    def parse_dms_string(dms_str: str) -> float:
        """
        解析度分秒字符串为十进制度数
        
        支持的格式：
        - 30°15'20.5"
        - 30d15m20.5s
        - 30:15:20.5
        - 30.255694 (十进制度数)
        
        Args:
            dms_str: 度分秒字符串
            
        Returns:
            float: 十进制度数
        """
        dms_str = dms_str.strip()
        
        # 尝试直接解析为浮点数
        try:
            return float(dms_str)
        except ValueError:
            pass
        
        # 解析度分秒格式
        import re
        
        # 匹配 30°15'20.5" 或 30d15m20.5s 格式
        pattern = r'([+-]?\d+)[°d:](\d+)[\'m:]([\d.]+)["s]?'
        match = re.match(pattern, dms_str)
        
        if match:
            degrees = int(match.group(1))
            minutes = int(match.group(2))
            seconds = float(match.group(3))
            
            sign = -1 if degrees < 0 else 1
            degrees = abs(degrees)
            
            return DMSConverter.dms_to_decimal(degrees, minutes, seconds, sign)
        
        raise ValueError(f"无法解析度分秒格式: {dms_str}")


# 便捷函数
def decimal_to_dms(decimal_degrees: float) -> DMS:
    """十进制度数转度分秒"""
    return DMSConverter.decimal_to_dms(decimal_degrees)


def dms_to_decimal(degrees: int, minutes: int, seconds: float, sign: int = 1) -> float:
    """度分秒转十进制度数"""
    return DMSConverter.dms_to_decimal(degrees, minutes, seconds, sign)
