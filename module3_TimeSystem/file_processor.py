"""
时间系统转换文件处理器
支持从文件批量导入时间数据并进行转换
"""

from typing import List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass

from .julian_day import JulianDay
from .gps_time import GPSTimeCalculator
from .models import GregorianTime, GPSTime


@dataclass
class TimeDataRecord:
    """时间数据记录"""
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: float
    line_number: int = 0
    
    def to_gregorian_time(self) -> GregorianTime:
        return GregorianTime(self.year, self.month, self.day, 
                           self.hour, self.minute, self.second)


@dataclass
class BatchConversionResult:
    """批量转换结果"""
    input_record: TimeDataRecord
    julian_day: float
    gps_week: int
    gps_seconds: float
    day_of_year: int
    fishing_status: str


class TimeFileProcessor:
    """时间数据文件处理器"""
    
    @staticmethod
    def parse_time_file(file_path: str) -> List[TimeDataRecord]:
        """
        解析时间数据文件
        
        文件格式：年 月 日 时 分 秒
        
        Args:
            file_path: 文件路径
            
        Returns:
            时间数据记录列表
        """
        records = []
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
        content = None
        
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    content = f.readlines()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            raise ValueError("无法读取文件，编码不支持")
        
        line_number = 0
        for line in content:
            line_number += 1
            line = line.strip()
            
            # 跳过空行和注释行
            if not line or line.startswith('#'):
                continue
            
            try:
                parts = line.split()
                if len(parts) < 6:
                    continue
                
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                hour = int(parts[3])
                minute = int(parts[4])
                second = float(parts[5])
                
                record = TimeDataRecord(
                    year=year, month=month, day=day,
                    hour=hour, minute=minute, second=second,
                    line_number=line_number
                )
                records.append(record)
                
            except (ValueError, IndexError) as e:
                # 跳过格式错误的行
                continue
        
        return records
    
    @staticmethod
    def batch_convert(records: List[TimeDataRecord]) -> List[BatchConversionResult]:
        """
        批量转换时间数据
        
        Args:
            records: 时间数据记录列表
            
        Returns:
            批量转换结果列表
        """
        results = []
        
        for record in records:
            # 计算儒略日
            jd = JulianDay.gregorian_to_jd(
                record.year, record.month, record.day,
                record.hour, record.minute, record.second
            )
            
            # 计算GPS时间
            gps_data = GPSTimeCalculator.jd_to_gps(jd)
            
            # 计算年积日
            day_of_year = JulianDay.day_of_year(record.year, record.month, record.day)
            
            # 计算三天打鱼两天晒网状态
            fishing_status = JulianDay.fishing_net_status(record.year, record.month, record.day)
            
            result = BatchConversionResult(
                input_record=record,
                julian_day=jd,
                gps_week=gps_data.week,
                gps_seconds=gps_data.seconds,
                day_of_year=day_of_year,
                fishing_status=fishing_status
            )
            results.append(result)
        
        return results
    
    @staticmethod
    def format_output(results: List[BatchConversionResult]) -> str:
        """
        按指导书要求格式化输出
        
        输出格式：
        -------JD-----------
        JD值1
        JD值2
        ...
        
        -------公历（年 月 日 时：分：秒）----------
        年 月 日 时 分 秒
        ...
        
        -------年积日----------
        第X日
        ...
        
        -------三天打鱼两天晒网----------
        打鱼/晒网
        ...
        
        -------GPS时间（周 周内秒）----------
        周 周内秒
        ...
        """
        lines = []
        
        # JD部分
        lines.append("-------JD-----------")
        for r in results:
            lines.append(f"{r.julian_day:.6f}")
        
        lines.append("")
        
        # 公历部分
        lines.append("-------公历（年 月 日 时：分：秒）----------")
        for r in results:
            rec = r.input_record
            lines.append(f"{rec.year} {rec.month} {rec.day} {rec.hour} {rec.minute} {int(rec.second)}")
        
        lines.append("")
        
        # 年积日部分
        lines.append("-------年积日----------")
        for r in results:
            lines.append(f"第{r.day_of_year}日")
        
        lines.append("")
        
        # 三天打鱼两天晒网部分
        lines.append("-------三天打鱼两天晒网----------")
        for r in results:
            lines.append(r.fishing_status)
        
        lines.append("")
        
        # GPS时间部分
        lines.append("-------GPS时间（周 周内秒）----------")
        for r in results:
            lines.append(f"{r.gps_week} {r.gps_seconds:.3f}")
        
        return "\n".join(lines)
    
    @staticmethod
    def process_file(file_path: str) -> Tuple[List[BatchConversionResult], str]:
        """
        处理时间数据文件的完整流程
        
        Args:
            file_path: 文件路径
            
        Returns:
            (结果列表, 格式化输出字符串)
        """
        records = TimeFileProcessor.parse_time_file(file_path)
        results = TimeFileProcessor.batch_convert(records)
        output = TimeFileProcessor.format_output(results)
        return results, output
