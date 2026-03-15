"""
日志管理模块
提供同时输出到控制台和文件的日志功能，支持按日期分割
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')


class SurveyLogger(logging.Logger):
    """
    自定义日志记录器
    扩展标准Logger，添加算法相关的日志方法
    """
    
    def log_algorithm_start(self, algorithm_name: str, params: dict) -> None:
        """
        记录算法开始执行
        
        Args:
            algorithm_name: 算法名称
            params: 算法参数
        """
        self.info(f"【算法开始】{algorithm_name}")
        self.debug(f"参数: {params}")
    
    def log_algorithm_end(self, algorithm_name: str, result_summary: str) -> None:
        """
        记录算法执行完成
        
        Args:
            algorithm_name: 算法名称
            result_summary: 结果摘要
        """
        self.info(f"【算法完成】{algorithm_name} - {result_summary}")
    
    def log_iteration(self, algorithm_name: str, iteration: int, 
                     residual: float, threshold: float) -> None:
        """
        记录迭代过程
        
        Args:
            algorithm_name: 算法名称
            iteration: 当前迭代次数
            residual: 当前残差
            threshold: 收敛阈值
        """
        self.debug(
            f"【迭代】{algorithm_name} - 第{iteration}次迭代, "
            f"残差={residual:.2e}, 阈值={threshold:.2e}"
        )
    
    def log_matrix_operation(self, operation: str, matrix_shape: tuple, 
                           condition_number: Optional[float] = None) -> None:
        """
        记录矩阵运算
        
        Args:
            operation: 运算类型
            matrix_shape: 矩阵形状
            condition_number: 条件数（可选）
        """
        msg = f"【矩阵运算】{operation}, 形状={matrix_shape}"
        if condition_number:
            msg += f", 条件数={condition_number:.2e}"
        self.debug(msg)
    
    def log_warning(self, module: str, message: str) -> None:
        """
        记录警告信息
        
        Args:
            module: 模块名称
            message: 警告内容
        """
        self.warning(f"【{module}】{message}")
    
    def log_error(self, module: str, message: str, exception: Optional[Exception] = None) -> None:
        """
        记录错误信息
        
        Args:
            module: 模块名称
            message: 错误内容
            exception: 异常对象（可选）
        """
        if exception:
            self.error(f"【{module}】{message}: {str(exception)}", exc_info=True)
        else:
            self.error(f"【{module}】{message}")


class LogManager:
    """
    日志管理器
    单例模式，确保整个应用使用统一的日志配置
    """
    _instance: Optional['LogManager'] = None
    _logger: Optional[SurveyLogger] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir: str = "logs", log_level: int = logging.DEBUG):
        """
        初始化日志管理器
        
        Args:
            log_dir: 日志文件存放目录
            log_level: 日志级别，默认为DEBUG
        """
        if self._logger is not None:
            return
            
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_level = log_level
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """配置日志记录器"""
        # 注册自定义Logger类
        logging.setLoggerClass(SurveyLogger)
        
        self._logger = logging.getLogger("SurveyDSP")
        self._logger.setLevel(self.log_level)
        
        # 清除已有处理器
        self._logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 1. 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # 2. 文件处理器（按日期分割）
        log_file = self.log_dir / f"survey_dsp_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
        
        # 3. 错误日志单独记录
        error_file = self.log_dir / f"survey_dsp_error_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self._logger.addHandler(error_handler)
        
        self._logger.info(f"日志系统初始化完成，日志目录: {self.log_dir.absolute()}")
    
    def get_logger(self, name: Optional[str] = None) -> SurveyLogger:
        """
        获取日志记录器
        
        Args:
            name: 子模块名称，用于区分不同模块的日志
            
        Returns:
            SurveyLogger: 配置好的日志记录器
        """
        if name:
            return self._logger.getChild(name)
        return self._logger


# 全局日志管理器实例
_log_manager: Optional[LogManager] = None


def get_logger(name: Optional[str] = None) -> SurveyLogger:
    """
    获取日志记录器的便捷函数
    
    Args:
        name: 子模块名称
        
    Returns:
        SurveyLogger: 配置好的日志记录器
    """
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager.get_logger(name)


def init_logging(log_dir: str = "logs", log_level: int = logging.DEBUG) -> LogManager:
    """
    初始化日志系统
    
    Args:
        log_dir: 日志文件存放目录
        log_level: 日志级别
        
    Returns:
        LogManager: 日志管理器实例
    """
    global _log_manager
    _log_manager = LogManager(log_dir, log_level)
    return _log_manager
