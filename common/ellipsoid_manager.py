"""
椭球参数管理模块
管理不同坐标系的椭球参数，支持从JSON配置文件读取
"""

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

from .logger import get_logger

logger = get_logger("EllipsoidManager")


@dataclass
class Ellipsoid:
    """
    椭球参数数据类
    
    Attributes:
        name: 椭球名称
        a: 长半轴（米）
        f: 扁率倒数
        description: 描述信息
    """
    name: str
    a: float
    f: float
    description: str = ""
    
    @property
    def b(self) -> float:
        """短半轴"""
        return self.a * (1 - 1/self.f)
    
    @property
    def e2(self) -> float:
        """第一偏心率的平方"""
        return (self.a**2 - self.b**2) / self.a**2
    
    @property
    def e2_prime(self) -> float:
        """第二偏心率的平方"""
        return (self.a**2 - self.b**2) / self.b**2
    
    @property
    def c(self) -> float:
        """极曲率半径"""
        return self.a**2 / self.b
    
    def get_N(self, B: float) -> float:
        """
        计算卯酉圈曲率半径
        
        Args:
            B: 纬度（弧度）
            
        Returns:
            卯酉圈曲率半径（米）
        """
        return self.a / math.sqrt(1 - self.e2 * math.sin(B)**2)
    
    def get_M(self, B: float) -> float:
        """
        计算子午圈曲率半径
        
        Args:
            B: 纬度（弧度）
            
        Returns:
            子午圈曲率半径（米）
        """
        return self.a * (1 - self.e2) / (1 - self.e2 * math.sin(B)**2)**1.5
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'name': self.name,
            'a': self.a,
            'f': self.f,
            'b': self.b,
            'e2': self.e2,
            'e2_prime': self.e2_prime,
            'description': self.description
        }


class EllipsoidManager:
    """
    椭球参数管理器
    单例模式管理所有椭球参数
    """
    _instance: Optional['EllipsoidManager'] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: str = "ellipsoid_config.json"):
        """
        初始化椭球管理器
        
        Args:
            config_path: 配置文件路径
        """
        if hasattr(self, '_initialized'):
            return
            
        self.config_path = Path(config_path)
        self._ellipsoids: Dict[str, Ellipsoid] = {}
        self._load_config()
        self._initialized = True
        logger.info(f"椭球管理器初始化完成，加载了 {len(self._ellipsoids)} 个坐标系")
    
    def _load_config(self) -> None:
        """从JSON文件加载椭球参数"""
        try:
            if not self.config_path.exists():
                logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
                self._load_default_config()
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            for name, params in config.items():
                self._ellipsoids[name] = Ellipsoid(
                    name=name,
                    a=params['a'],
                    f=params['f'],
                    description=params.get('description', '')
                )
            
            logger.debug(f"成功加载 {len(self._ellipsoids)} 个椭球参数")
            
        except Exception as e:
            logger.error("加载椭球配置失败", e)
            self._load_default_config()
    
    def _load_default_config(self) -> None:
        """加载默认配置"""
        default_ellipsoids = {
            'WGS84': Ellipsoid('WGS84', 6378137.0, 298.257223563, '默认WGS84'),
            'CGCS2000': Ellipsoid('CGCS2000', 6378137.0, 298.257222101, '默认CGCS2000'),
        }
        self._ellipsoids.update(default_ellipsoids)
        logger.info("已加载默认椭球配置")
    
    def get_ellipsoid(self, name: str) -> Ellipsoid:
        """
        获取指定椭球参数
        
        Args:
            name: 椭球名称
            
        Returns:
            Ellipsoid: 椭球参数对象
            
        Raises:
            KeyError: 如果椭球不存在
        """
        if name not in self._ellipsoids:
            available = ', '.join(self._ellipsoids.keys())
            raise KeyError(f"未知的椭球类型: {name}。可用类型: {available}")
        return self._ellipsoids[name]
    
    def add_ellipsoid(self, name: str, a: float, f: float, 
                     description: str = "") -> None:
        """
        添加自定义椭球参数
        
        Args:
            name: 椭球名称
            a: 长半轴
            f: 扁率倒数
            description: 描述信息
        """
        self._ellipsoids[name] = Ellipsoid(name, a, f, description)
        logger.info(f"添加自定义椭球: {name}")
    
    def list_ellipsoids(self) -> Dict[str, str]:
        """
        列出所有可用的椭球类型
        
        Returns:
            Dict[str, str]: 名称和描述的映射
        """
        return {name: ell.description for name, ell in self._ellipsoids.items()}
    
    def save_config(self, path: Optional[str] = None) -> None:
        """
        保存当前配置到JSON文件
        
        Args:
            path: 保存路径，默认为原配置文件路径
        """
        save_path = Path(path) if path else self.config_path
        
        config = {}
        for name, ell in self._ellipsoids.items():
            config[name] = {
                'a': ell.a,
                'f': ell.f,
                'description': ell.description
            }
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"配置已保存到: {save_path}")


# 便捷函数
def get_ellipsoid(name: str) -> Ellipsoid:
    """获取椭球参数的便捷函数"""
    manager = EllipsoidManager()
    return manager.get_ellipsoid(name)


def list_ellipsoids() -> Dict[str, str]:
    """列出所有椭球类型的便捷函数"""
    manager = EllipsoidManager()
    return manager.list_ellipsoids()
