"""
格雷厄姆扫描算法模块
提供点集排序和凸包计算功能
"""

import numpy as np
from typing import List, Tuple
from dataclasses import dataclass

from common.logger import get_logger

logger = get_logger("GrahamScan")


@dataclass
class Point:
    """点数据类"""
    x: float
    y: float
    idx: int = 0
    
    def __repr__(self):
        return f"Point({self.x:.3f}, {self.y:.3f})"


class GrahamScan:
    """
    格雷厄姆扫描算法
    用于对点集进行排序，确保构成简单多边形
    """
    
    def __init__(self):
        """初始化格雷厄姆扫描器"""
        self.logger = logger
    
    def sort_points(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        对点集进行极角排序
        
        Args:
            points: 点集列表 [(x1, y1), (x2, y2), ...]
            
        Returns:
            排序后的点集
        """
        if len(points) < 3:
            return points
        
        # 转换为Point对象
        point_objects = [Point(x, y, i) for i, (x, y) in enumerate(points)]
        
        # 找到基准点（y最小，若相同则x最小）
        pivot = min(point_objects, key=lambda p: (p.y, p.x))
        self.logger.debug(f"基准点: {pivot}")
        
        # 按极角排序
        def polar_angle(p: Point) -> float:
            """计算相对于基准点的极角"""
            return np.arctan2(p.y - pivot.y, p.x - pivot.x)
        
        # 排序：先按极角，极角相同按距离
        def sort_key(p: Point):
            angle = polar_angle(p)
            dist = (p.x - pivot.x)**2 + (p.y - pivot.y)**2
            return (angle, dist)
        
        sorted_points = sorted(point_objects, key=sort_key)
        
        self.logger.debug(f"排序完成，共 {len(sorted_points)} 个点")
        
        # 转换回元组列表
        return [(p.x, p.y) for p in sorted_points]
    
    def convex_hull(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        计算凸包
        
        Args:
            points: 点集列表
            
        Returns:
            凸包顶点列表（逆时针顺序）
        """
        if len(points) < 3:
            return points
        
        # 转换为Point对象
        point_objects = [Point(x, y, i) for i, (x, y) in enumerate(points)]
        
        # 找到基准点
        pivot = min(point_objects, key=lambda p: (p.y, p.x))
        
        # 按极角排序
        def polar_angle(p: Point) -> float:
            return np.arctan2(p.y - pivot.y, p.x - pivot.x)
        
        sorted_points = sorted(point_objects, key=lambda p: (polar_angle(p), 
                            (p.x - pivot.x)**2 + (p.y - pivot.y)**2))
        
        # 构建凸包
        hull = []
        for p in sorted_points:
            # 当栈中至少有2个点，且新点使栈顶三点形成右转时，弹出栈顶
            while len(hull) >= 2:
                p1 = hull[-2]
                p2 = hull[-1]
                cross = self._cross_product(p1, p2, p)
                if cross <= 0:  # 右转或共线，弹出
                    hull.pop()
                else:
                    break
            hull.append(p)
        
        self.logger.debug(f"凸包计算完成，顶点数: {len(hull)}")
        
        return [(p.x, p.y) for p in hull]
    
    def _cross_product(self, p1: Point, p2: Point, p3: Point) -> float:
        """
        计算叉积 (p2-p1) × (p3-p1)
        
        Returns:
            正值：左转（逆时针）
            负值：右转（顺时针）
            零：共线
        """
        return (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)
    
    def is_simple_polygon(self, points: List[Tuple[float, float]]) -> bool:
        """
        检查是否为简单多边形（边不相交）
        
        Args:
            points: 点集列表
            
        Returns:
            是否为简单多边形
        """
        n = len(points)
        if n < 3:
            return False
        
        # 检查每条边是否与其他边相交（不包括相邻边）
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            
            for j in range(i + 2, n):
                if j == (i - 1 + n) % n:  # 跳过相邻边
                    continue
                
                p3 = points[j]
                p4 = points[(j + 1) % n]
                
                if self._segments_intersect(p1, p2, p3, p4):
                    return False
        
        return True
    
    def _segments_intersect(self, p1: Tuple[float, float], p2: Tuple[float, float],
                           p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
        """
        检查两条线段是否相交
        
        Args:
            p1, p2: 第一条线段的端点
            p3, p4: 第二条线段的端点
            
        Returns:
            是否相交
        """
        def cross(ax, ay, bx, by):
            return ax * by - ay * bx
        
        def direction(px, py, qx, qy, rx, ry):
            return cross(qx - px, qy - py, rx - px, ry - py)
        
        d1 = direction(p3[0], p3[1], p4[0], p4[1], p1[0], p1[1])
        d2 = direction(p3[0], p3[1], p4[0], p4[1], p2[0], p2[1])
        d3 = direction(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
        d4 = direction(p1[0], p1[1], p2[0], p2[1], p4[0], p4[1])
        
        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
           ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True
        
        if d1 == 0 and self._on_segment(p3, p4, p1):
            return True
        if d2 == 0 and self._on_segment(p3, p4, p2):
            return True
        if d3 == 0 and self._on_segment(p1, p2, p3):
            return True
        if d4 == 0 and self._on_segment(p1, p2, p4):
            return True
        
        return False
    
    def _on_segment(self, p1: Tuple[float, float], p2: Tuple[float, float],
                   p: Tuple[float, float]) -> bool:
        """检查点p是否在线段p1p2上"""
        return min(p1[0], p2[0]) <= p[0] <= max(p1[0], p2[0]) and \
               min(p1[1], p2[1]) <= p[1] <= max(p1[1], p2[1])
