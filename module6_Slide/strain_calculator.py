"""
应变计算模块
计算监测点对之间的相对应变
"""

import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MonitoringPoint:
    """监测点"""
    id: str
    epoch: int
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'MonitoringPoint') -> float:
        """计算到另一点的距离"""
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 +
            (self.z - other.z) ** 2
        )


@dataclass
class PointPair:
    """监测点对"""
    id: str
    point1_id: str
    point2_id: str


@dataclass
class StrainResult:
    """应变计算结果"""
    pair_id: str
    epoch1: int
    epoch2: int
    distance1: float
    distance2: float
    strain: float
    
    def __str__(self) -> str:
        return (f"点对 {self.pair_id}: "
                f"期{self.epoch1}->期{self.epoch2}, "
                f"距离 {self.distance1:.4f}->{self.distance2:.4f}, "
                f"应变 {self.strain:.6f}")


class StrainCalculator:
    """应变计算器"""
    
    def __init__(self):
        self.points: Dict[str, List[MonitoringPoint]] = {}
        self.pairs: List[PointPair] = []
    
    def add_point(self, point: MonitoringPoint):
        """添加监测点"""
        if point.id not in self.points:
            self.points[point.id] = []
        self.points[point.id].append(point)
    
    def add_pair(self, pair: PointPair):
        """添加监测点对"""
        self.pairs.append(pair)
    
    def calculate_strain(self, pair: PointPair, epoch1: int, epoch2: int) -> Optional[StrainResult]:
        """
        计算点对在两个时期的应变
        
        Args:
            pair: 监测点对
            epoch1: 第一期
            epoch2: 第二期
            
        Returns:
            StrainResult 或 None
        """
        p1_list = self.points.get(pair.point1_id, [])
        p2_list = self.points.get(pair.point2_id, [])
        
        p1_e1 = next((p for p in p1_list if p.epoch == epoch1), None)
        p1_e2 = next((p for p in p1_list if p.epoch == epoch2), None)
        p2_e1 = next((p for p in p2_list if p.epoch == epoch1), None)
        p2_e2 = next((p for p in p2_list if p.epoch == epoch2), None)
        
        if not all([p1_e1, p1_e2, p2_e1, p2_e2]):
            return None
        
        distance1 = p1_e1.distance_to(p2_e1)
        distance2 = p1_e2.distance_to(p2_e2)
        
        if distance1 < 1e-10:
            return None
        
        strain = (distance2 - distance1) / distance1
        
        return StrainResult(
            pair_id=pair.id,
            epoch1=epoch1,
            epoch2=epoch2,
            distance1=distance1,
            distance2=distance2,
            strain=strain
        )
    
    def calculate_all_strains(self) -> List[StrainResult]:
        """计算所有点对的应变"""
        results = []
        
        epochs = set()
        for point_list in self.points.values():
            for p in point_list:
                epochs.add(p.epoch)
        epochs = sorted(epochs)
        
        for pair in self.pairs:
            for i in range(len(epochs) - 1):
                result = self.calculate_strain(pair, epochs[i], epochs[i + 1])
                if result:
                    results.append(result)
        
        return results
    
    @classmethod
    def from_data(cls, points_data: List[Dict], pairs_data: List[Dict]) -> 'StrainCalculator':
        """
        从数据创建应变计算器
        
        Args:
            points_data: 点数据列表 [{'id': 'M01', 'epoch': 1, 'x': 100, 'y': 200, 'z': 50}, ...]
            pairs_data: 点对数据列表 [{'id': 'PAIR01', 'point1': 'M01', 'point2': 'M02'}, ...]
            
        Returns:
            StrainCalculator
        """
        calculator = cls()
        
        for p in points_data:
            point = MonitoringPoint(
                id=p['id'],
                epoch=p['epoch'],
                x=p['x'],
                y=p['y'],
                z=p['z']
            )
            calculator.add_point(point)
        
        for pair in pairs_data:
            pp = PointPair(
                id=pair['id'],
                point1_id=pair['point1'],
                point2_id=pair['point2']
            )
            calculator.add_pair(pp)
        
        return calculator
