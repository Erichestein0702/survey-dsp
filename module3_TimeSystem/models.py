"""
时间系统转换数据模型
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class TimeType(Enum):
    """时间类型"""
    GREGORIAN = "gregorian"     # 公历（年月日时分秒）
    JULIAN_DAY = "jd"           # 儒略日
    GPS_TIME = "gps"            # GPS时间（周+周内秒）


@dataclass
class GregorianTime:
    """公历时间"""
    year: int
    month: int
    day: int
    hour: int = 0
    minute: int = 0
    second: float = 0.0
    
    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d} {self.hour:02d}:{self.minute:02d}:{self.second:06.3f}"


@dataclass
class GPSTime:
    """GPS时间"""
    week: int
    seconds: float
    
    def __str__(self) -> str:
        days = int(self.seconds // 86400)
        remaining = self.seconds % 86400
        hours = int(remaining // 3600)
        remaining %= 3600
        minutes = int(remaining // 60)
        secs = remaining % 60
        return f"GPS Week {self.week}, Day {days}, {hours:02d}:{minutes:02d}:{secs:06.3f}"


@dataclass
class TimeConversionResult:
    """时间转换结果"""
    input_type: TimeType
    output_type: TimeType
    gregorian: Optional[GregorianTime] = None
    julian_day: Optional[float] = None
    gps_time: Optional[GPSTime] = None
    
    def __str__(self) -> str:
        lines = []
        lines.append(f"输入类型: {self.input_type.value}")
        lines.append(f"输出类型: {self.output_type.value}")
        lines.append("-" * 40)
        if self.gregorian:
            lines.append(f"公历时间: {self.gregorian}")
        if self.julian_day is not None:
            lines.append(f"儒略日: {self.julian_day:.6f}")
        if self.gps_time:
            lines.append(f"GPS时间: {self.gps_time}")
        return "\n".join(lines)
