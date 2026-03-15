"""
滑坡变形分析核心模块
计算位移速度、相对应变，提供预警功能
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from common.logger import get_logger
from common.parser import DataParser
from common.exporter import Exporter

logger = get_logger("DeformationAnalyzer")


@dataclass
class DeformationResult:
    """变形分析结果"""
    velocities: Dict[str, float]  # 各点位移速度
    strains: Dict[str, float]     # 各点相对应变
    max_velocity_point: str       # 最大速度点
    max_strain_point: str         # 最大应变点
    warnings: List[str]           # 预警信息


class DeformationAnalyzer:
    """变形分析器"""
    
    def __init__(self):
        self.parser = DataParser()
        self.exporter = Exporter()
        logger.info("变形分析器初始化完成")
    
    def analyze(self, data) -> DeformationResult:
        """分析变形数据"""
        
        if isinstance(data, dict):
            df_data = []
            for point_id, epochs in data.items():
                for epoch, x, y in epochs:
                    df_data.append({'ID': point_id, 'Epoch': epoch, 'X': x, 'Y': y})
            data = pd.DataFrame(df_data)
        
        logger.log_algorithm_start("滑坡变形分析", {'数据点数': len(data)})
        
        velocities = {}
        strains = {}
        
        if data.empty or len(data) == 0:
            logger.warning("输入数据为空")
            return DeformationResult(velocities, strains, "", "", ["输入数据为空"])
        
        for point_id in data['ID'].unique():
            point_data = data[data['ID'] == point_id].sort_values('Epoch')
            if len(point_data) < 2:
                logger.debug(f"点 {point_id} 数据不足2期，跳过")
                continue
            
            # 计算位移速度
            v = self._calculate_velocity(point_data)
            velocities[point_id] = v
            
            # 计算相对应变
            epsilon = self._calculate_strain(point_data)
            strains[point_id] = epsilon
        
        max_v_point = max(velocities.items(), key=lambda x: x[1])[0] if velocities else ""
        max_e_point = max(strains.items(), key=lambda x: abs(x[1]))[0] if strains else ""
        
        warnings = self._check_warnings(velocities, strains)
        
        if not velocities:
            warnings.append("没有足够的数据进行变形分析")
            logger.log_algorithm_end("滑坡变形分析", "数据不足")
        else:
            logger.log_algorithm_end("滑坡变形分析", 
                                    f"最大速度={max(velocities.values()):.6f}, 最大应变={max(abs(v) for v in strains.values()):.6f}")
        
        return DeformationResult(velocities, strains, max_v_point, max_e_point, warnings)
    
    def _calculate_velocity(self, point_data: pd.DataFrame) -> float:
        """计算位移速度"""
        if 'Z' in point_data.columns:
            coords = point_data[['X', 'Y', 'Z']].values
        else:
            coords = point_data[['X', 'Y']].values
        epochs = point_data['Epoch'].values
        
        # 计算总位移和总时间
        total_disp = 0.0
        total_time = 0.0
        
        for i in range(len(coords) - 1):
            dx = coords[i+1] - coords[i]
            disp = np.sqrt(np.sum(dx**2))
            dt = epochs[i+1] - epochs[i]
            
            total_disp += disp
            total_time += dt
        
        return total_disp / total_time if total_time > 0 else 0.0
    
    def _calculate_strain(self, point_data: pd.DataFrame) -> float:
        """计算相对应变"""
        if 'Z' in point_data.columns:
            coords = point_data[['X', 'Y', 'Z']].values
        else:
            coords = point_data[['X', 'Y']].values
        
        if len(coords) < 2:
            return 0.0
        
        # 计算首尾位移差相对于初始位置的比例
        initial_pos = coords[0]
        final_pos = coords[-1]
        displacement = np.sqrt(np.sum((final_pos - initial_pos)**2))
        
        # 归一化（假设基准长度为1）
        return displacement / 1000.0  # 简化为mm/m
    
    def _check_warnings(self, velocities: Dict, strains: Dict) -> List[str]:
        """检查预警条件"""
        warnings = []
        
        # 速度阈值 (mm/期)
        v_threshold = 5.0
        # 应变阈值
        e_threshold = 0.001
        
        for pid, v in velocities.items():
            if v * 1000 > v_threshold:  # 转换为mm
                warnings.append(f"点{pid}速度异常: {v*1000:.2f} mm/期")
        
        for pid, e in strains.items():
            if abs(e) > e_threshold:
                warnings.append(f"点{pid}应变异常: {e:.6f}")
        
        return warnings
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """加载时序数据"""
        result = self.parser.parse_timeseries_data(file_path)
        return result.data
    
    def generate_report(self, result: DeformationResult) -> str:
        """生成报告"""
        report = self.exporter.create_report_header("滑坡监测报告", "模块6 - 滑坡监测")
        
        report += "## 位移速度\n\n"
        report += "| 点号 | 速度 (mm/期) |\n"
        report += "|------|-------------|\n"
        for pid, v in result.velocities.items():
            report += f"| {pid} | {v*1000:.3f} |\n"
        
        report += f"\n**最大速度点**: {result.max_velocity_point}\n\n"
        
        report += "## 相对应变\n\n"
        report += "| 点号 | 应变 |\n"
        report += "|------|------|\n"
        for pid, e in result.strains.items():
            report += f"| {pid} | {e:.6f} |\n"
        
        if result.warnings:
            report += "\n## 预警信息\n\n"
            for w in result.warnings:
                report += f"- ⚠️ {w}\n"
        
        return report
