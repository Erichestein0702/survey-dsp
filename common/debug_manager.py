"""
调试管理模块
提供统一的调试机制，支持各模块的调试信息收集和输出
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from .logger import get_logger

logger = get_logger("DebugManager")


@dataclass
class DebugInfo:
    """调试信息数据类"""
    module_name: str
    operation: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    execution_time: float
    timestamp: str
    errors: List[str]
    warnings: List[str]


class DebugManager:
    """
    调试管理器
    统一管理各模块的调试信息
    """
    
    _instance: Optional['DebugManager'] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, debug_dir: str = "logs/debug"):
        if hasattr(self, '_initialized'):
            return
            
        self.debug_dir = Path(debug_dir)
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        self.debug_history: List[DebugInfo] = []
        self._initialized = True
        
        logger.info(f"调试管理器初始化完成，调试目录: {self.debug_dir.absolute()}")
    
    def log_operation(self, module_name: str, operation: str,
                     input_data: Dict[str, Any], 
                     output_data: Dict[str, Any],
                     execution_time: float,
                     errors: List[str] = None,
                     warnings: List[str] = None) -> DebugInfo:
        """
        记录操作调试信息
        
        Args:
            module_name: 模块名称
            operation: 操作名称
            input_data: 输入数据摘要
            output_data: 输出数据摘要
            execution_time: 执行时间(秒)
            errors: 错误信息列表
            warnings: 警告信息列表
            
        Returns:
            DebugInfo: 调试信息对象
        """
        debug_info = DebugInfo(
            module_name=module_name,
            operation=operation,
            input_data=input_data,
            output_data=output_data,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat(),
            errors=errors or [],
            warnings=warnings or []
        )
        
        self.debug_history.append(debug_info)
        
        # 写入日志
        logger.debug(f"[{module_name}] {operation} 完成，耗时: {execution_time:.3f}s")
        
        if errors:
            for error in errors:
                logger.error(f"[{module_name}] {operation} 错误: {error}")
        
        if warnings:
            for warning in warnings:
                logger.warning(f"[{module_name}] {operation} 警告: {warning}")
        
        return debug_info
    
    def save_debug_report(self, module_name: str = None) -> str:
        """
        保存调试报告
        
        Args:
            module_name: 模块名称，None表示保存所有
            
        Returns:
            str: 报告文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if module_name:
            filename = f"debug_{module_name}_{timestamp}.json"
            data = [asdict(d) for d in self.debug_history if d.module_name == module_name]
        else:
            filename = f"debug_all_{timestamp}.json"
            data = [asdict(d) for d in self.debug_history]
        
        filepath = self.debug_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"调试报告已保存: {filepath}")
        return str(filepath)
    
    def get_module_stats(self, module_name: str) -> Dict[str, Any]:
        """
        获取模块统计信息
        
        Args:
            module_name: 模块名称
            
        Returns:
            Dict: 统计信息
        """
        module_logs = [d for d in self.debug_history if d.module_name == module_name]
        
        if not module_logs:
            return {}
        
        total_time = sum(d.execution_time for d in module_logs)
        total_errors = sum(len(d.errors) for d in module_logs)
        total_warnings = sum(len(d.warnings) for d in module_logs)
        
        return {
            'module_name': module_name,
            'total_operations': len(module_logs),
            'total_execution_time': total_time,
            'average_execution_time': total_time / len(module_logs),
            'total_errors': total_errors,
            'total_warnings': total_warnings
        }
    
    def clear_history(self):
        """清空调试历史"""
        self.debug_history.clear()
        logger.info("调试历史已清空")


# 装饰器：自动记录函数执行信息
def debug_operation(operation_name: str = None):
    """
    调试装饰器
    自动记录函数的执行时间、输入输出等信息
    
    Args:
        operation_name: 操作名称，默认为函数名
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            module_name = func.__module__.split('.')[-1]
            op_name = operation_name or func.__name__
            
            start_time = time.time()
            errors = []
            warnings = []
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 构建输入输出摘要
                input_summary = {
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
                
                output_summary = {
                    'type': type(result).__name__,
                    'has_result': result is not None
                }
                
                # 记录调试信息
                debug_mgr = DebugManager()
                debug_mgr.log_operation(
                    module_name=module_name,
                    operation=op_name,
                    input_data=input_summary,
                    output_data=output_summary,
                    execution_time=execution_time,
                    errors=errors,
                    warnings=warnings
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                errors.append(str(e))
                
                debug_mgr = DebugManager()
                debug_mgr.log_operation(
                    module_name=module_name,
                    operation=op_name,
                    input_data={'args_count': len(args)},
                    output_data={'error': str(e)},
                    execution_time=execution_time,
                    errors=errors
                )
                
                raise
        
        return wrapper
    return decorator


# 全局调试管理器实例
_debug_manager: Optional[DebugManager] = None


def get_debug_manager() -> DebugManager:
    """获取调试管理器实例"""
    global _debug_manager
    if _debug_manager is None:
        _debug_manager = DebugManager()
    return _debug_manager
