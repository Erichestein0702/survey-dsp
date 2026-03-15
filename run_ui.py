"""
测绘综合实习DSP系统 - UI启动入口
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.logger import init_logging

init_logging()

from ui.main_window import run_app

if __name__ == '__main__':
    run_app()
