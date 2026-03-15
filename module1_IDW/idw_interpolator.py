"""
IDW插值核心算法
"""

import math
from typing import List, Optional, Tuple
import numpy as np

from .models import KnownPoint, TargetPoint, IDWResult, IDWBatchResult


class IDWInterpolator:
    """反距离加权插值器"""
    
    def __init__(self, known_points: List[KnownPoint], power: float = 2.0, 
                 search_radius: Optional[float] = None, n_neighbors: Optional[int] = None):
        """
        初始化IDW插值器
        
        Args:
            known_points: 已知采样点列表
            power: 权指数，默认为2
            search_radius: 搜索半径，None表示使用所有点
            n_neighbors: 选择最近的n个点进行插值，None表示使用所有点
        """
        self.known_points = known_points
        self.power = power
        self.search_radius = search_radius
        self.n_neighbors = n_neighbors
        
        self._points_array = np.array([[p.x, p.y, p.z] for p in known_points])
    
    @staticmethod
    def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """计算两点间的平面距离"""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    @staticmethod
    def calculate_weight(distance: float, power: float = 2.0) -> float:
        """
        计算权值
        
        Args:
            distance: 距离
            power: 权指数
            
        Returns:
            权值
        """
        if distance < 1e-10:
            return float('inf')
        return 1.0 / (distance ** power)
    
    def _get_nearby_points(self, x: float, y: float) -> List[Tuple[int, float]]:
        """
        获取附近的已知点
        
        Args:
            x: 目标点X坐标
            y: 目标点Y坐标
            
        Returns:
            [(点索引, 距离), ...]
        """
        distances = []
        for i, p in enumerate(self.known_points):
            d = self.calculate_distance(x, y, p.x, p.y)
            if self.search_radius is None or d <= self.search_radius:
                distances.append((i, d))
        
        if self.n_neighbors is not None and len(distances) > self.n_neighbors:
            distances.sort(key=lambda x: x[1])
            distances = distances[:self.n_neighbors]
        
        return distances
    
    def interpolate(self, target: TargetPoint) -> IDWResult:
        """
        对单个点进行IDW插值
        
        Args:
            target: 待插值点
            
        Returns:
            IDWResult
        """
        nearby = self._get_nearby_points(target.x, target.y)
        
        if not nearby:
            raise ValueError(f"点 {target.id} 附近没有已知点")
        
        for idx, dist in nearby:
            if dist < 1e-10:
                z = self.known_points[idx].z
                return IDWResult(
                    target_point=target,
                    interpolated_z=z,
                    distances=[dist],
                    weights=[float('inf')],
                    used_points=[self.known_points[idx].id],
                    power=self.power
                )
        
        weights = []
        weighted_sum = 0.0
        weight_sum = 0.0
        distances = []
        used_points = []
        
        for idx, dist in nearby:
            w = self.calculate_weight(dist, self.power)
            weights.append(w)
            weighted_sum += w * self.known_points[idx].z
            weight_sum += w
            distances.append(dist)
            used_points.append(self.known_points[idx].id)
        
        interpolated_z = weighted_sum / weight_sum
        
        target.z = interpolated_z
        
        return IDWResult(
            target_point=target,
            interpolated_z=interpolated_z,
            distances=distances,
            weights=weights,
            used_points=used_points,
            power=self.power
        )
    
    def interpolate_batch(self, targets: List[TargetPoint], n_values: List[int] = None) -> dict:
        """
        批量IDW插值
        
        Args:
            targets: 待插值点列表
            n_values: 不同的n_neighbors值列表，用于题目要求的n=4,5,6
            
        Returns:
            字典，key为n值，value为IDWBatchResult
        """
        if n_values is None:
            n_values = [self.n_neighbors] if self.n_neighbors else [None]
        
        results_dict = {}
        for n in n_values:
            self.n_neighbors = n
            results = []
            for target in targets:
                result = self.interpolate(target)
                results.append(result)
            
            results_dict[n] = IDWBatchResult(
                results=results,
                power=self.power,
                total_points=len(self.known_points),
                interpolated_points=len(targets)
            )
        
        self.n_neighbors = n_values[0] if n_values else None
        return results_dict
    
    @classmethod
    def from_file(cls, filepath: str, power: float = 2.0, 
                  search_radius: Optional[float] = None, 
                  n_neighbors: Optional[int] = None) -> 'IDWInterpolator':
        """
        从文件创建插值器
        
        Args:
            filepath: 数据文件路径
            power: 权指数
            search_radius: 搜索半径
            n_neighbors: 选择最近的n个点
            
        Returns:
            IDWInterpolator
        """
        known_points = []
        target_points = []
        section = None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    if '已知' in line or '测站' in line or '格式' in line:
                        section = 'known'
                    elif '待插值' in line or '目标' in line:
                        section = 'target'
                    continue
                
                parts = line.split()
                if len(parts) >= 4 and section == 'known':
                    point = KnownPoint(
                        id=parts[0],
                        x=float(parts[1]),
                        y=float(parts[2]),
                        z=float(parts[3])
                    )
                    known_points.append(point)
                elif len(parts) >= 3 and section == 'target':
                    point = TargetPoint(
                        id=parts[0],
                        x=float(parts[1]),
                        y=float(parts[2])
                    )
                    target_points.append(point)
        
        return cls(known_points, power, search_radius, n_neighbors), target_points
