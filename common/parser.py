"""
多源数据解析引擎
支持 .txt, .csv, .dat 等多种格式的测绘数据文件解析
自动识别编码、分隔符，提供数据校验功能
"""

import re
import charset_normalizer
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict, Optional, Union
from dataclasses import dataclass
from io import StringIO

from .logger import get_logger

logger = get_logger("DataParser")


@dataclass
class ParseResult:
    """
    解析结果数据类
    
    Attributes:
        data: 解析后的数据DataFrame
        errors: 错误信息列表
        encoding: 检测到的编码
        delimiter: 检测到的分隔符
        row_count: 总行数
        valid_row_count: 有效行数
    """
    data: pd.DataFrame
    errors: List[str]
    encoding: str
    delimiter: str
    row_count: int
    valid_row_count: int


class DataParser:
    """
    数据解析器
    提供多格式测绘数据文件的解析功能
    """
    
    # 支持的编码列表（按尝试顺序）
    SUPPORTED_ENCODINGS = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']
    
    # 标准列名映射（支持中英文）
    COLUMN_MAPPINGS = {
        # ID列
        'id': 'ID', 'ID': 'ID', '编号': 'ID', '点号': 'ID', 'name': 'ID',
        # X坐标
        'x': 'X', 'X': 'X', 'east': 'X', '东': 'X', '东坐标': 'X',
        # Y坐标
        'y': 'Y', 'Y': 'Y', 'north': 'Y', '北': 'Y', '北坐标': 'Y',
        # Z坐标/高程
        'z': 'Z', 'Z': 'Z', 'h': 'Z', 'H': 'Z', 'height': 'Z', '高程': 'Z', '高': 'Z',
        # 高程异常
        'zeta': 'Zeta', 'Zeta': 'Zeta', '高程异常': 'Zeta', '异常': 'Zeta',
        # 时间
        'time': 'Time', 'Time': 'Time', '时间': 'Time', '日期': 'Time',
        # 期数
        'epoch': 'Epoch', 'Epoch': 'Epoch', '期': 'Epoch', '期数': 'Epoch',
    }
    
    def __init__(self):
        """初始化数据解析器"""
        logger.info("数据解析器初始化完成")
    
    def parse_file(self, file_path: Union[str, Path]) -> ParseResult:
        """
        解析数据文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            ParseResult: 解析结果
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持或解析失败
        """
        file_path = Path(file_path)
        logger.info(f"开始解析文件: {file_path}")
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 检测编码
        encoding = self._detect_encoding(file_path)
        logger.debug(f"检测到编码: {encoding}")
        
        # 读取并过滤文件内容
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            # 过滤注释行和空行
            filtered_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    filtered_lines.append(line)
            
            if not filtered_lines:
                raise ValueError("文件内容为空或只有注释")
            
            content = ''.join(filtered_lines)
            
        except Exception as e:
            logger.error(f"DataParser 读取文件失败: {file_path} - {e}")
            raise ValueError(f"无法读取文件: {e}")
        
        # 检测分隔符并解析
        delimiter = self._detect_delimiter_from_content(content)
        logger.debug(f"检测到分隔符: '{delimiter}'")
        
        try:
            df = pd.read_csv(
                StringIO(content),
                delimiter=delimiter,
                dtype=str,
                skipinitialspace=True
            )
        except Exception as e:
            logger.error(f"DataParser 解析CSV失败: {e}")
            raise ValueError(f"无法解析文件内容: {e}")
        
        row_count = len(df)
        logger.debug(f"原始数据行数: {row_count}")
        
        # 标准化列名
        df = self._standardize_columns(df)
        
        # 数据校验和转换
        df, errors = self._validate_and_convert(df)
        
        valid_row_count = len(df)
        logger.info(
            f"文件解析完成: {valid_row_count}/{row_count} 行有效, "
            f"{len(errors)} 个错误"
        )
        
        return ParseResult(
            data=df,
            errors=errors,
            encoding=encoding,
            delimiter=delimiter,
            row_count=row_count,
            valid_row_count=valid_row_count
        )
    
    def _detect_encoding(self, file_path: Path) -> str:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            检测到的编码名称
        """
        # 首先尝试charset_normalizer检测
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(4096)
                result = charset_normalizer.from_bytes(raw_data)
                if result.best():
                    encoding = result.best().encoding
                    if encoding:
                        return encoding
        except Exception:
            pass
        
        # 按顺序尝试支持的编码
        for encoding in self.SUPPORTED_ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1024)
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # 默认返回utf-8
        logger.warning("DataParser 无法确定编码，默认使用utf-8")
        return 'utf-8'
    
    def _detect_delimiter_from_content(self, content: str) -> str:
        """
        从内容中检测分隔符
        
        Args:
            content: 文件内容
            
        Returns:
            检测到的分隔符
        """
        lines = content.strip().split('\n')
        if not lines:
            return ','
        
        # 取前几行作为样本
        sample_lines = lines[:min(10, len(lines))]
        
        # 测试不同分隔符
        delimiters = [',', '\t', ';', ' ']
        delimiter_counts = {}
        
        for delim in delimiters:
            counts = []
            for line in sample_lines:
                if delim == ' ':
                    # 对于空格，计算连续空格分隔的字段数
                    fields = len(line.split())
                else:
                    fields = line.count(delim) + 1
                counts.append(fields)
            
            # 检查一致性
            if len(set(counts)) == 1 and counts[0] > 1:
                delimiter_counts[delim] = counts[0]
        
        # 选择字段数最多的分隔符
        if delimiter_counts:
            return max(delimiter_counts.items(), key=lambda x: x[1])[0]
        
        return ','  # 默认逗号
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化列名
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        new_columns = {}
        for col in df.columns:
            col_clean = col.strip().lower()
            if col_clean in self.COLUMN_MAPPINGS:
                new_columns[col] = self.COLUMN_MAPPINGS[col_clean]
            else:
                new_columns[col] = col.strip()
        
        df = df.rename(columns=new_columns)
        return df
    
    def _validate_and_convert(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        数据校验和类型转换
        
        Args:
            df: 原始DataFrame
            
        Returns:
            (有效数据DataFrame, 错误信息列表)
        """
        errors = []
        valid_data = {}
        
        # 识别数值列和非数值列
        numeric_columns = []
        string_columns = []
        for col in df.columns:
            if col in ['X', 'Y', 'Z', 'Zeta']:
                numeric_columns.append(col)
            else:
                string_columns.append(col)
        
        # 初始化有效数据字典
        for col in df.columns:
            valid_data[col] = []
        
        for idx, row in df.iterrows():
            row_errors = []
            row_valid = True
            
            # 检查空值
            if row.isnull().all():
                continue  # 跳过完全空行
            
            # 处理数值列
            for col in numeric_columns:
                if col in row.index:
                    try:
                        value = str(row[col]).strip()
                        if value:
                            valid_data[col].append(float(value))
                        else:
                            row_errors.append(f"行{idx+1}: 列'{col}'为空")
                            row_valid = False
                    except (ValueError, TypeError) as e:
                        row_errors.append(f"行{idx+1}: 列'{col}'无法转换为数值: {row[col]}")
                        row_valid = False
                else:
                    row_valid = False
            
            # 处理字符串列
            for col in string_columns:
                if col in row.index:
                    valid_data[col].append(str(row[col]).strip())
                else:
                    valid_data[col].append('')
            
            if row_errors:
                errors.extend(row_errors)
            
            # 如果数值列有错误，移除这行数据
            if not row_valid:
                for col in valid_data:
                    if len(valid_data[col]) > len(valid_data.get(numeric_columns[0], [])):
                        valid_data[col].pop()
        
        # 构建结果DataFrame
        if valid_data and numeric_columns and len(valid_data[numeric_columns[0]]) > 0:
            result_df = pd.DataFrame(valid_data)
            # 确保数值列为float64
            for col in numeric_columns:
                if col in result_df.columns:
                    result_df[col] = result_df[col].astype(np.float64)
        else:
            result_df = pd.DataFrame(columns=df.columns)
        
        return result_df, errors
    
    def parse_coordinates(self, file_path: Union[str, Path]) -> ParseResult:
        """
        专门解析坐标数据（XYZ格式）
        
        Args:
            file_path: 文件路径
            
        Returns:
            ParseResult: 解析结果，包含X, Y, Z列
        """
        result = self.parse_file(file_path)
        
        # 检查必要的列
        required_cols = ['X', 'Y', 'Z']
        missing_cols = [col for col in required_cols if col not in result.data.columns]
        
        if missing_cols:
            logger.warning(
                f"DataParser 坐标数据缺少列: {missing_cols}，可用列: {list(result.data.columns)}"
            )
        
        return result
    
    def parse_elevation_data(self, file_path: Union[str, Path]) -> ParseResult:
        """
        专门解析高程拟合数据（XYZ + Zeta格式）
        
        Args:
            file_path: 文件路径
            
        Returns:
            ParseResult: 解析结果，包含X, Y, Z, Zeta列
        """
        result = self.parse_file(file_path)
        
        # 检查必要的列
        required_cols = ['X', 'Y', 'Zeta']
        missing_cols = [col for col in required_cols if col not in result.data.columns]
        
        if missing_cols:
            logger.warning(
                f"DataParser 高程数据缺少列: {missing_cols}"
            )
        
        return result
    
    def parse_timeseries_data(self, file_path: Union[str, Path]) -> ParseResult:
        """
        专门解析时序数据（XYZ + Time/Epoch格式）
        
        Args:
            file_path: 文件路径
            
        Returns:
            ParseResult: 解析结果
        """
        result = self.parse_file(file_path)
        
        # 检查时序标识列
        if 'Time' not in result.data.columns and 'Epoch' not in result.data.columns:
            logger.warning(
                f"DataParser 时序数据缺少时间/期数列，可用列: {list(result.data.columns)}"
            )
        
        return result
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的文件格式
        
        Returns:
            支持的扩展名列表
        """
        return ['.txt', '.csv', '.dat', '.xyz', '.pts']


# 便捷函数
def parse_file(file_path: Union[str, Path]) -> ParseResult:
    """解析文件的便捷函数"""
    parser = DataParser()
    return parser.parse_file(file_path)


def parse_coordinates(file_path: Union[str, Path]) -> ParseResult:
    """解析坐标数据的便捷函数"""
    parser = DataParser()
    return parser.parse_coordinates(file_path)
