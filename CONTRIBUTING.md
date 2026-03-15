# Contributing to Survey DSP

感谢你考虑为测绘综合实习 DSP 数据处理平台做出贡献！

## 如何贡献

### 报告 Bug

如果你发现了 bug，请通过 [GitHub Issues](../../issues) 提交报告。提交前请：

1. 搜索现有的 issues，确认该问题尚未被报告
2. 使用 Bug 报告模板，包含以下信息：
   - 操作系统和 Python 版本
   - 复现步骤
   - 期望行为和实际行为
   - 相关日志或截图

### 提出新功能

欢迎提出新功能建议！请通过 [GitHub Issues](../../issues) 提交，并说明：

1. 功能描述
2. 使用场景
3. 可能的实现思路

### 提交代码

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature-name`
3. 进行代码修改
4. 确保代码风格一致
5. 提交更改：`git commit -m 'Add some feature'`
6. 推送分支：`git push origin feature/your-feature-name`
7. 提交 Pull Request

## 代码规范

### Python 代码风格

- 遵循 PEP 8 编码规范
- 使用 4 空格缩进
- 函数和类添加文档字符串
- 变量命名使用 snake_case，类命名使用 PascalCase

### 提交信息规范

- 使用简洁明了的提交信息
- 建议格式：`<type>: <description>`
- 类型包括：`feat`（新功能）、`fix`（修复）、`docs`（文档）、`refactor`（重构）、`test`（测试）

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/your-username/survey-dsp.git
cd survey-dsp

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行测试
python test_all_modules.py

# 启动应用
python run_ui.py
```

## 项目结构

```
survey-dsp/
├── common/           # 通用组件（日志、解析器、矩阵引擎等）
├── module1_IDW/      # IDW 插值模块
├── module2_GPS_Elevation/  # GPS 高程拟合模块
├── module3_TimeSystem/     # 时间系统转换模块
├── module4_Area/     # 面积计算模块
├── module5_Cord/     # 坐标转换模块
├── module6_Slide/    # 滑坡监测模块
├── ui/               # 用户界面
├── test_data/        # 测试数据
└── logs/             # 日志目录
```

## 联系方式

如有问题，请联系维护者：erichestein

---

再次感谢你的贡献！
