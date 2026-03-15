"""
全模块测试脚本
验证6个模块的修复是否正确
"""

import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.logger import get_logger, init_logging
from common.debug_manager import get_debug_manager

logger = get_logger("TestAllModules")

# 定义状态符号
CHECK = "[OK]"
CROSS = "[FAIL]"


def test_module1_idw():
    """测试模块1: IDW插值 - n=4,5,6对比"""
    print("\n" + "="*70)
    print("测试模块1: IDW插值 (n=4,5,6对比)")
    print("="*70)
    
    try:
        from module1_IDW.idw_interpolator import IDWInterpolator
        from module1_IDW.models import KnownPoint, TargetPoint
        
        # 创建测试数据
        known_points = [
            KnownPoint("P1", 0, 0, 10.0),
            KnownPoint("P2", 10, 0, 12.0),
            KnownPoint("P3", 10, 10, 15.0),
            KnownPoint("P4", 0, 10, 13.0),
            KnownPoint("P5", 5, 5, 14.0),
            KnownPoint("P6", 15, 5, 16.0),
        ]
        
        target_points = [
            TargetPoint("Q1", 5, 2),
            TargetPoint("Q2", 8, 8),
        ]
        
        # 测试n=4,5,6对比
        interpolator = IDWInterpolator(known_points, power=2.0)
        results_dict = interpolator.interpolate_batch(target_points, n_values=[4, 5, 6])
        
        print(f"{CHECK} 已知点数: {len(known_points)}")
        print(f"{CHECK} 待插值点数: {len(target_points)}")
        print(f"{CHECK} n值对比结果:")
        
        for n, batch_result in results_dict.items():
            print(f"  n={n}: 插值完成，共{len(batch_result.results)}个点")
        
        print(f"{CHECK} 模块1测试通过")
        return True
        
    except Exception as e:
        print(f"{CROSS} 模块1测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_module2_gps_elevation():
    """测试模块2: GPS高程拟合 - 三种方法对比"""
    print("\n" + "="*70)
    print("测试模块2: GPS高程拟合 (三种方法对比)")
    print("="*70)
    
    try:
        from module2_GPS_Elevation.elevation_fitter import ElevationFitter
        import numpy as np
        
        # 创建测试数据（12个已知点）
        np.random.seed(42)
        X = np.random.uniform(0, 100, 12)
        Y = np.random.uniform(0, 100, 12)
        Zeta = 0.5 * X + 0.3 * Y + 0.001 * X**2 + np.random.normal(0, 0.01, 12)
        
        fitter = ElevationFitter()
        result = fitter.fit(X, Y, Zeta, center_coordinates=True)
        
        print(f"{CHECK} 已知点数: {len(X)}")
        print(f"{CHECK} 拟合方法数: {len(result.all_results)}")
        print(f"{CHECK} 最优方法: {result.best_model_name}")
        print(f"{CHECK} 最优RMS: {result.best_model_result.rms*1000:.3f} mm")
        
        for name, model_result in result.all_results.items():
            print(f"  {name}: RMS={model_result.rms*1000:.3f} mm")
        
        print(f"{CHECK} 模块2测试通过")
        return True
        
    except Exception as e:
        print(f"{CROSS} 模块2测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_module3_time_system():
    """测试模块3: 时间系统转换 - 文件批量处理"""
    print("\n" + "="*70)
    print("测试模块3: 时间系统转换 (文件批量处理)")
    print("="*70)
    
    try:
        from module3_TimeSystem.file_processor import TimeFileProcessor
        
        # 创建测试文件
        test_file = "test_time_data.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# 测试时间数据\n")
            f.write("2026 3 11 8 30 0\n")
            f.write("2026 3 12 12 0 0\n")
            f.write("2026 3 13 18 45 30\n")
        
        # 测试文件处理
        results, output = TimeFileProcessor.process_file(test_file)
        
        print(f"{CHECK} 测试文件: {test_file}")
        print(f"{CHECK} 处理记录数: {len(results)}")
        print(f"{CHECK} 输出格式预览:")
        print("-" * 40)
        print(output[:500])
        print("-" * 40)
        
        # 清理测试文件
        os.remove(test_file)
        
        print(f"{CHECK} 模块3测试通过")
        return True
        
    except Exception as e:
        print(f"{CROSS} 模块3测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_module4_area():
    """测试模块4: 面积计算 - 海伦公式"""
    print("\n" + "="*70)
    print("测试模块4: 面积计算 (海伦公式)")
    print("="*70)
    
    try:
        from module4_Area.heron_calculator import HeronCalculator
        
        # 8个顶点的多边形
        vertices = [
            (0, 0),      # A
            (10, 0),     # B
            (15, 5),     # C
            (12, 10),    # D
            (8, 12),     # E
            (2, 10),     # F
            (-2, 5),     # G
            (0, 2),      # H
        ]
        
        names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        
        result = HeronCalculator.calculate_from_vertices(vertices, names)
        
        print(f"{CHECK} 顶点数: {result.vertex_count}")
        print(f"{CHECK} 三角形数: {len(result.triangles)}")
        print(f"{CHECK} 总面积: {result.total_area:.4f} m²")
        
        for tri in result.triangles:
            print(f"  三角形{tri.index} ({tri.vertex_a}-{tri.vertex_b}-{tri.vertex_c}): "
                  f"面积={tri.area:.4f} m²")
        
        print(f"{CHECK} 模块4测试通过")
        return True
        
    except Exception as e:
        print(f"{CROSS} 模块4测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_module5_coord():
    """测试模块5: 坐标转换 - 克拉索夫斯基椭球、度分秒格式"""
    print("\n" + "="*70)
    print("测试模块5: 坐标转换 (克拉索夫斯基椭球、度分秒格式)")
    print("="*70)
    
    try:
        from module5_Cord.blh_converter import BLHConverter
        from module5_Cord.dms_converter import DMSConverter
        from common.ellipsoid_manager import EllipsoidManager
        
        # 测试克拉索夫斯基椭球
        manager = EllipsoidManager()
        krassovsky = manager.get_ellipsoid("Krassovsky")
        
        print(f"{CHECK} 克拉索夫斯基椭球:")
        print(f"  长半轴 a = {krassovsky.a}")
        print(f"  扁率 f = {krassovsky.f}")
        
        # 测试XYZ转BLH
        converter = BLHConverter(krassovsky)
        X, Y, Z = -2422455.7116, 5377816.7730, 2434562.7366
        blh = converter.xyz_to_blh(X, Y, Z)
        
        print(f"{CHECK} XYZ转BLH:")
        print(f"  输入: ({X}, {Y}, {Z})")
        print(f"  输出: B={blh.B_deg:.6f}°, L={blh.L_deg:.6f}°, H={blh.H:.3f}m")
        
        # 测试度分秒格式
        dms_str = DMSConverter.format_blh_dms(blh.B_deg, blh.L_deg, blh.H)
        print(f"{CHECK} 度分秒格式: {dms_str}")
        
        print(f"{CHECK} 模块5测试通过")
        return True
        
    except Exception as e:
        print(f"{CROSS} 模块5测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_module6_landslide():
    """测试模块6: 滑坡监测 - 仅XY二维"""
    print("\n" + "="*70)
    print("测试模块6: 滑坡监测 (仅XY二维)")
    print("="*70)
    
    try:
        from module6_Slide.deformation_analyzer import DeformationAnalyzer
        import pandas as pd
        
        # 创建测试数据（仅XY）
        data = pd.DataFrame({
            'ID': ['M01', 'M01', 'M01', 'M02', 'M02', 'M02'],
            'Epoch': [1, 2, 3, 1, 2, 3],
            'X': [100.0, 100.05, 100.12, 200.0, 199.98, 199.95],
            'Y': [50.0, 50.03, 50.08, 150.0, 150.02, 150.05],
        })
        
        analyzer = DeformationAnalyzer()
        result = analyzer.analyze(data)
        
        print(f"{CHECK} 监测点数: {len(result.velocities)}")
        print(f"{CHECK} 变形速度:")
        for pid, v in result.velocities.items():
            print(f"  {pid}: {v*1000:.3f} mm/期")
        
        print(f"{CHECK} 最大速度点: {result.max_velocity_point}")
        
        print(f"{CHECK} 模块6测试通过")
        return True
        
    except Exception as e:
        print(f"{CROSS} 模块6测试失败: {str(e)}")
        traceback.print_exc()
        return False


def test_debug_manager():
    """测试调试管理器"""
    print("\n" + "="*70)
    print("测试调试管理器")
    print("="*70)
    
    try:
        from common.debug_manager import get_debug_manager
        
        debug_mgr = get_debug_manager()
        
        # 记录一些调试信息
        debug_mgr.log_operation(
            module_name="Test",
            operation="test_operation",
            input_data={'test': 'data'},
            output_data={'result': 'success'},
            execution_time=0.5
        )
        
        # 保存调试报告
        report_path = debug_mgr.save_debug_report()
        
        print(f"{CHECK} 调试管理器初始化成功")
        print(f"{CHECK} 调试历史数: {len(debug_mgr.debug_history)}")
        print(f"{CHECK} 调试报告已保存: {report_path}")
        
        print(f"{CHECK} 调试管理器测试通过")
        return True
        
    except Exception as e:
        print(f"{CROSS} 调试管理器测试失败: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("="*70)
    print("测绘综合实习 - 全模块修复验证测试")
    print("="*70)
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 初始化日志
    init_logging()
    
    # 运行所有测试
    results = {
        "模块1-IDW插值": test_module1_idw(),
        "模块2-GPS高程拟合": test_module2_gps_elevation(),
        "模块3-时间系统转换": test_module3_time_system(),
        "模块4-面积计算": test_module4_area(),
        "模块5-坐标转换": test_module5_coord(),
        "模块6-滑坡监测": test_module6_landslide(),
        "调试管理器": test_debug_manager(),
    }
    
    # 输出测试结果汇总
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"{name}: {status}")
    
    print("-"*70)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n所有测试通过！修复验证成功。")
    else:
        print(f"\n{total - passed} 个测试失败，请检查修复。")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
