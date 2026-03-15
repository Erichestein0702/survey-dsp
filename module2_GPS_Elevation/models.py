"""
高程拟合模型定义
包含三种拟合模型：平面拟合，二次曲面拟合，四参数曲面拟合
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple, List
from dataclasses import dataclass

from common.logger import get_logger

logger = get_logger("GPS_Models")


@dataclass
class ModelResult:
    """模型拟合结果"""
    model_name: str
    coefficients: np.ndarray
    residuals: np.ndarray
    rms: float
    design_matrix: np.ndarray


class FittingModel(ABC):
    """拟合模型基类"""
    
    def __init__(self, name: str):
        """
        初始化模型
        
        Args:
            name: 模型名称
        """
        self.name = name
        self.logger = get_logger(f"GPS_Models.{name}")
    
    @abstractmethod
    def build_design_matrix(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        """
        构建设计矩阵
        
        Args:
            X: X坐标数组
            Y: Y坐标数组
            
        Returns:
            设计矩阵A
        """
        pass
    
    @abstractmethod
    def evaluate(self, X: np.ndarray, Y: np.ndarray, 
                coefficients: np.ndarray) -> np.ndarray:
        """
        使用模型计算高程异常值
        
        Args:
            X: X坐标数组
            Y: Y坐标数组
            coefficients: 模型系数
            
        Returns:
            计算的高程异常值
        """
        pass
    
    @property
    @abstractmethod
    def num_params(self) -> int:
        """模型参数个数"""
        pass
    
    @property
    @abstractmethod
    def complexity(self) -> int:
        """模型复杂度（用于模型选择）"""
        pass


class PlaneModel(FittingModel):
    """
    多项式平面拟合模型
    ζ = a₀ + a₁X + a₂Y
    """
    
    def __init__(self):
        super().__init__("平面拟合")
    
    def build_design_matrix(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        """构建设计矩阵 [1, X, Y]"""
        n = len(X)
        A = np.column_stack([
            np.ones(n, dtype=np.float64),
            X,
            Y
        ])
        self.logger.debug(f"构建设计矩阵: 形状={A.shape}")
        return A
    
    def evaluate(self, X: np.ndarray, Y: np.ndarray, 
                coefficients: np.ndarray) -> np.ndarray:
        """计算 ζ = a₀ + a₁X + a₂Y"""
        a0, a1, a2 = coefficients
        return a0 + a1 * X + a2 * Y
    
    @property
    def num_params(self) -> int:
        return 3
    
    @property
    def complexity(self) -> int:
        return 1  # 最简单
    
    def __repr__(self):
        return "PlaneModel(ζ = a₀ + a₁X + a₂Y)"


class QuadraticModel(FittingModel):
    """
    二次曲面拟合模型
    ζ = a₀ + a₁X + a₂Y + a₃X² + a₄XY + a₅Y²
    """
    
    def __init__(self):
        super().__init__("二次曲面拟合")
    
    def build_design_matrix(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        """构建设计矩阵 [1, X, Y, X², XY, Y²]"""
        n = len(X)
        A = np.column_stack([
            np.ones(n, dtype=np.float64),
            X,
            Y,
            X**2,
            X * Y,
            Y**2
        ])
        self.logger.debug(f"构建设计矩阵: 形状={A.shape}")
        return A
    
    def evaluate(self, X: np.ndarray, Y: np.ndarray, 
                coefficients: np.ndarray) -> np.ndarray:
        """计算 ζ = a₀ + a₁X + a₂Y + a₃X² + a₄XY + a₅Y²"""
        a0, a1, a2, a3, a4, a5 = coefficients
        return a0 + a1*X + a2*Y + a3*X**2 + a4*X*Y + a5*Y**2
    
    @property
    def num_params(self) -> int:
        return 6
    
    @property
    def complexity(self) -> int:
        return 3  # 最复杂
    
    def __repr__(self):
        return "QuadraticModel(ζ = a₀ + a₁X + a₂Y + a₃X² + a₄XY + a₅Y²)"


class FourParamModel(FittingModel):
    """
    四参数曲面拟合模型
    ζ = a₀ + a₁X + a₂Y + a₃XY
    """
    
    def __init__(self):
        super().__init__("四参数曲面拟合")
    
    def build_design_matrix(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        """构建设计矩阵 [1, X, Y, XY]"""
        n = len(X)
        A = np.column_stack([
            np.ones(n, dtype=np.float64),
            X,
            Y,
            X * Y
        ])
        self.logger.debug(f"构建设计矩阵: 形状={A.shape}")
        return A
    
    def evaluate(self, X: np.ndarray, Y: np.ndarray, 
                coefficients: np.ndarray) -> np.ndarray:
        """计算 ζ = a₀ + a₁X + a₂Y + a₃XY"""
        a0, a1, a2, a3 = coefficients
        return a0 + a1*X + a2*Y + a3*X*Y
    
    @property
    def num_params(self) -> int:
        return 4
    
    @property
    def complexity(self) -> int:
        return 2  # 中等复杂度
    
    def __repr__(self):
        return "FourParamModel(ζ = a₀ + a₁X + a₂Y + a₃XY)"


# 模型工厂函数
def get_model(model_type: str) -> FittingModel:
    """
    根据类型获取模型实例
    
    Args:
        model_type: 模型类型 ('plane', 'quadratic', 'four_param')
        
    Returns:
        FittingModel: 模型实例
    """
    models = {
        'plane': PlaneModel,
        'quadratic': QuadraticModel,
        'four_param': FourParamModel
    }
    
    if model_type not in models:
        raise ValueError(f"未知模型类型: {model_type}。可用类型: {list(models.keys())}")
    
    return models[model_type]()


def get_all_models() -> List[FittingModel]:
    """获取所有可用模型"""
    return [PlaneModel(), QuadraticModel(), FourParamModel()]
