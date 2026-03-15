"""
IDW插值数据模型
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class KnownPoint:
    """已知采样点"""
    id: str
    x: float
    y: float
    z: float
    
    def __str__(self) -> str:
        return f"{self.id}: ({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"


@dataclass
class TargetPoint:
    """待插值点"""
    id: str
    x: float
    y: float
    z: Optional[float] = None
    
    def __str__(self) -> str:
        if self.z is not None:
            return f"{self.id}: ({self.x:.3f}, {self.y:.3f}) -> {self.z:.3f}"
        return f"{self.id}: ({self.x:.3f}, {self.y:.3f}) -> 待计算"


@dataclass
class IDWResult:
    """IDW插值结果"""
    target_point: TargetPoint
    interpolated_z: float
    distances: List[float]
    weights: List[float]
    used_points: List[str]
    power: float
    
    def __str__(self) -> str:
        lines = [
            f"点 {self.target_point.id} 插值结果:",
            f"  坐标: ({self.target_point.x:.3f}, {self.target_point.y:.3f})",
            f"  插值高程: {self.interpolated_z:.6f}",
            f"  权指数: {self.power}",
            f"  使用点数: {len(self.used_points)}",
            f"  最近距离: {min(self.distances):.6f}" if self.distances else "  无距离数据"
        ]
        return "\n".join(lines)


@dataclass
class IDWBatchResult:
    """批量IDW插值结果"""
    results: List[IDWResult]
    power: float
    total_points: int
    interpolated_points: int
    
    def __str__(self) -> str:
        lines = [
            "=" * 50,
            "IDW插值批量计算结果",
            "=" * 50,
            f"权指数: {self.power}",
            f"已知点数: {self.total_points}",
            f"插值点数: {self.interpolated_points}",
            "-" * 50
        ]
        for r in self.results:
            lines.append(f"{r.target_point.id}: {r.interpolated_z:.6f}")
        lines.append("=" * 50)
        return "\n".join(lines)
