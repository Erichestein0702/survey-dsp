"""
矩阵计算核心模块
提供高精度矩阵运算，包含法方程求解、岭估计、SVD分解等功能
支持病态矩阵检测与处理
"""

import numpy as np
from typing import Tuple, Optional, Dict, Literal
from dataclasses import dataclass
from enum import Enum

from .logger import get_logger

logger = get_logger("MatrixEngine")


class SolverMethod(Enum):
    """求解方法枚举"""
    DIRECT = "direct"           # 直接求解
    RIDGE = "ridge"             # 岭估计
    SVD = "svd"                 # SVD分解


@dataclass
class SolverResult:
    """
    求解结果数据类
    
    Attributes:
        x: 参数解向量
        residuals: 残差向量
        condition_number: 条件数
        method_used: 使用的方法
        rms: 中误差
        rank: 矩阵秩（SVD时使用）
        singular_values: 奇异值（SVD时使用）
        warning_message: 警告信息
    """
    x: np.ndarray
    residuals: np.ndarray
    condition_number: float
    method_used: SolverMethod
    rms: float
    rank: Optional[int] = None
    singular_values: Optional[np.ndarray] = None
    warning_message: Optional[str] = None


class MatrixEngine:
    """
    矩阵计算引擎
    提供稳定的高精度矩阵运算
    """
    
    # 数值阈值常量
    COND_THRESHOLD_WARN = 1e8      # 条件数警告阈值
    COND_THRESHOLD_RIDGE = 1e10    # 触发岭估计阈值
    COND_THRESHOLD_SVD = 1e12      # 触发SVD阈值
    RIDGE_LAMBDA = 1e-6            # 岭估计参数
    SVD_TOLERANCE = 1e-10          # SVD截断容差
    
    def __init__(self):
        """初始化矩阵引擎"""
        logger.info("矩阵引擎初始化完成")
    
    def solve_normal_equation(self, A: np.ndarray, b: np.ndarray,
                            force_method: Optional[SolverMethod] = None) -> SolverResult:
        """
        求解法方程 Ax = b
        
        自动选择最优求解策略：
        1. 条件数 < 1e8：直接求解
        2. 1e8 <= 条件数 < 1e12：岭估计
        3. 条件数 >= 1e12：SVD分解
        
        Args:
            A: 设计矩阵 (m x n)
            b: 观测向量 (m,)
            force_method: 强制使用指定方法（用于调试）
            
        Returns:
            SolverResult: 求解结果
        """
        # 确保双精度
        A = np.asarray(A, dtype=np.float64)
        b = np.asarray(b, dtype=np.float64)
        
        m, n = A.shape
        logger.log_matrix_operation("法方程求解", (m, n))
        
        # 构建法方程
        N = A.T @ A
        U = A.T @ b
        
        # 计算条件数
        cond = np.linalg.cond(N)
        logger.log_matrix_operation("条件数计算", N.shape, cond)
        
        # 确定求解方法
        if force_method:
            method = force_method
        elif cond < self.COND_THRESHOLD_RIDGE:
            method = SolverMethod.DIRECT
        elif cond < self.COND_THRESHOLD_SVD:
            method = SolverMethod.RIDGE
        else:
            method = SolverMethod.SVD
        
        # 根据方法求解
        if method == SolverMethod.DIRECT:
            result = self._solve_direct(N, U, A, b, cond)
        elif method == SolverMethod.RIDGE:
            result = self._solve_ridge(N, U, A, b, cond)
        else:  # SVD
            result = self._solve_svd(A, b, cond)
        
        # 记录结果
        logger.log_algorithm_end(
            "法方程求解",
            f"方法={result.method_used.value}, 条件数={cond:.2e}, RMS={result.rms:.2e}"
        )
        
        return result
    
    def _solve_direct(self, N: np.ndarray, U: np.ndarray,
                     A: np.ndarray, b: np.ndarray, cond: float) -> SolverResult:
        """直接求解法方程"""
        try:
            x = np.linalg.solve(N, U)
            residuals = A @ x - b
            rms = np.sqrt(np.sum(residuals**2) / (A.shape[0] - A.shape[1]))
            
            warning = None
            if cond > self.COND_THRESHOLD_WARN:
                warning = f"矩阵条件数较大({cond:.2e})，结果可能存在数值不稳定"
                logger.log_warning("MatrixEngine", warning)
            
            return SolverResult(
                x=x,
                residuals=residuals,
                condition_number=cond,
                method_used=SolverMethod.DIRECT,
                rms=rms,
                warning_message=warning
            )
        except np.linalg.LinAlgError as e:
            logger.log_error("MatrixEngine", "直接求解失败，切换到岭估计", e)
            return self._solve_ridge(N, U, A, b, cond)
    
    def _solve_ridge(self, N: np.ndarray, U: np.ndarray,
                    A: np.ndarray, b: np.ndarray, cond: float,
                    lambda_val: float = None) -> SolverResult:
        """
        岭估计求解
        
        通过引入正则化参数改善矩阵条件数
        """
        if lambda_val is None:
            lambda_val = self.RIDGE_LAMBDA
        
        logger.log_warning(
            "MatrixEngine",
            f"使用岭估计求解，λ={lambda_val}, 原条件数={cond:.2e}"
        )
        
        # 构建岭回归矩阵
        n = N.shape[0]
        N_ridge = N + lambda_val * np.eye(n)
        
        # 求解
        x = np.linalg.solve(N_ridge, U)
        residuals = A @ x - b
        rms = np.sqrt(np.sum(residuals**2) / (A.shape[0] - A.shape[1]))
        
        # 计算改善后的条件数
        new_cond = np.linalg.cond(N_ridge)
        logger.log_matrix_operation("岭估计后条件数", N_ridge.shape, new_cond)
        
        return SolverResult(
            x=x,
            residuals=residuals,
            condition_number=cond,
            method_used=SolverMethod.RIDGE,
            rms=rms,
            warning_message=f"使用岭估计(λ={lambda_val})改善数值稳定性"
        )
    
    def _solve_svd(self, A: np.ndarray, b: np.ndarray, cond: float) -> SolverResult:
        """
        SVD分解求解
        
        最稳健的求解方法，通过截断小奇异值处理病态矩阵
        """
        logger.log_warning(
            "MatrixEngine",
            f"使用SVD分解求解，条件数={cond:.2e}"
        )
        
        # SVD分解: A = U @ S @ Vh
        U, s, Vh = np.linalg.svd(A, full_matrices=False)
        
        # 确定有效秩（截断小奇异值）
        tol = self.SVD_TOLERANCE * s[0]  # 相对容差
        rank = np.sum(s > tol)
        
        logger.debug(f"SVD奇异值: {s}")
        logger.debug(f"有效秩: {rank}/{len(s)}")
        
        # 截断SVD求解
        s_inv = np.zeros_like(s)
        s_inv[:rank] = 1.0 / s[:rank]
        
        # x = V @ S^+ @ U^T @ b
        x = Vh.T @ np.diag(s_inv) @ U.T @ b
        
        residuals = A @ x - b
        rms = np.sqrt(np.sum(residuals**2) / (A.shape[0] - rank))
        
        return SolverResult(
            x=x,
            residuals=residuals,
            condition_number=cond,
            method_used=SolverMethod.SVD,
            rms=rms,
            rank=rank,
            singular_values=s,
            warning_message=f"使用SVD分解(秩={rank}/{len(s)})处理严重病态矩阵"
        )
    
    def solve_svd(self, N: np.ndarray, U: np.ndarray) -> Optional[np.ndarray]:
        """
        使用SVD分解求解法方程 Nx = U
        
        Args:
            N: 法方程系数矩阵
            U: 法方程常数项
            
        Returns:
            解向量x，如果失败返回None
        """
        try:
            # SVD分解: N = U @ S @ Vh
            U_mat, s, Vh = np.linalg.svd(N, full_matrices=False)
            
            # 确定有效秩（截断小奇异值）
            tol = self.SVD_TOLERANCE * s[0] if len(s) > 0 else self.SVD_TOLERANCE
            rank = np.sum(s > tol)
            
            if rank < len(s):
                logger.log_warning(
                    "MatrixEngine",
                    f"SVD截断: 有效秩={rank}/{len(s)}"
                )
            
            # 截断SVD求解
            s_inv = np.zeros_like(s)
            s_inv[:rank] = 1.0 / s[:rank]
            
            # x = V @ S^+ @ U^T @ U
            x = Vh.T @ np.diag(s_inv) @ U_mat.T @ U
            
            return x
            
        except Exception as e:
            logger.log_error("MatrixEngine", "SVD求解失败", e)
            return None
    
    def calculate_rms(self, residuals: np.ndarray, n: int, k: int) -> float:
        """
        计算中误差（Root Mean Square）
        
        Args:
            residuals: 残差向量
            n: 观测数
            k: 参数个数
            
        Returns:
            RMS值
        """
        if n <= k:
            return np.inf
        return np.sqrt(np.sum(residuals**2) / (n - k))
    
    def calculate_condition_number(self, A: np.ndarray) -> float:
        """
        计算矩阵条件数
        
        Args:
            A: 输入矩阵
            
        Returns:
            条件数
        """
        return np.linalg.cond(A)
    
    def check_matrix_health(self, A: np.ndarray) -> Dict:
        """
        检查矩阵健康状况
        
        Args:
            A: 输入矩阵
            
        Returns:
            包含条件数、秩、奇异值等信息的字典
        """
        A = np.asarray(A, dtype=np.float64)
        
        cond = np.linalg.cond(A)
        rank = np.linalg.matrix_rank(A)
        _, s, _ = np.linalg.svd(A)
        
        health_status = "健康"
        if cond > self.COND_THRESHOLD_SVD:
            health_status = "严重病态"
        elif cond > self.COND_THRESHOLD_RIDGE:
            health_status = "病态"
        elif cond > self.COND_THRESHOLD_WARN:
            health_status = "轻度病态"
        
        return {
            'condition_number': cond,
            'rank': rank,
            'full_rank': rank == min(A.shape),
            'singular_values': s,
            'health_status': health_status,
            'recommendation': self._get_recommendation(cond)
        }
    
    def _get_recommendation(self, cond: float) -> str:
        """根据条件数给出建议"""
        if cond < self.COND_THRESHOLD_WARN:
            return "矩阵健康，可直接求解"
        elif cond < self.COND_THRESHOLD_RIDGE:
            return "建议检查数据质量，可考虑岭估计"
        elif cond < self.COND_THRESHOLD_SVD:
            return "建议使用岭估计改善数值稳定性"
        else:
            return "矩阵严重病态，必须使用SVD分解"


# 便捷函数
def solve_least_squares(A: np.ndarray, b: np.ndarray,
                       force_method: Optional[SolverMethod] = None) -> SolverResult:
    """
    最小二乘求解便捷函数
    
    Args:
        A: 设计矩阵
        b: 观测向量
        force_method: 强制使用的方法
        
    Returns:
        SolverResult: 求解结果
    """
    engine = MatrixEngine()
    return engine.solve_normal_equation(A, b, force_method)
