"""
测绘综合实习 - DSP算法集成平台
主程序入口

功能模块：
- 模块1：IDW插值
- 模块2：GPS高程拟合
- 模块3：时间系统转换
- 模块4：多边形面积计算
- 模块5：坐标转换
- 模块6：滑坡监测

作者：SurveyDSP Team
版本：1.0.1
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置NumPy打印选项
import numpy as np
np.set_printoptions(precision=10, suppress=True)

from common.logger import get_logger, init_logging

logger = get_logger('Main')


def print_banner():
    """打印程序横幅"""
    banner = """
    ================================================================
    
           测绘综合实习 - DSP算法集成平台 v1.0.1
    
  功能模块：
    [1] IDW插值           - 反距离加权插值
    [2] GPS高程拟合      - 平面/二次曲面/四参数模型
    [3] 时间系统转换     - 儒略日/年积日/打鱼晒网
    [4] 多边形面积计算   - 支持任意简单多边形
    [5] 坐标转换         - XYZ/BLH/NEU/3种椭球
    [6] 滑坡监测         - 变形分析与预警系统
    
    ================================================================
    """
    print(banner)


def run_all_tests():
    """运行所有模块测试"""
    print("\n" + "="*70)
    print("运行所有模块测试")
    print("="*70)
    
    try:
        import test_all_modules
        print("\n✓ 所有模块测试通过!")
        return True
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        print(f"\n✗ 测试失败: {str(e)}")
        return False


def show_menu():
    """显示主菜单"""
    print("\n" + "="*60)
    print("主菜单")
    print("="*60)
    print("1. 运行所有模块测试")
    print("2. 运行UI界面")
    print("0. 退出程序")
    print("="*60)


def run_ui():
    """运行UI界面"""
    print("\n启动UI界面...")
    try:
        from ui.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        import sys
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"UI启动失败: {str(e)}")
        print(f"UI启动失败: {str(e)}")
        return False
    return True


def main():
    """主函数"""
    # 初始化日志系统
    init_logging()
    
    # 打印横幅
    print_banner()
    
    logger.info("程序启动")
    
    while True:
        show_menu()
        choice = input("请输入选项 (0-2): ").strip()
        
        if choice == '0':
            print("\n感谢使用，再见！")
            logger.info("程序退出")
            break
        elif choice == '1':
            run_all_tests()
        elif choice == '2':
            run_ui()
        else:
            print("\n无效选项，请重新输入")
        
        input("\n按回车键继续...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常: {str(e)}")
        raise
