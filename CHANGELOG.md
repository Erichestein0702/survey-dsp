# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-03-14

### Added

- IDW 插值模块：支持 n=4,5,6 邻近点对比分析
- GPS 高程拟合模块：平面拟合、四参数拟合、二次曲面拟合三种方法
- 时间系统转换模块：公历时间、儒略日、GPS时间互转
- 多边形面积计算模块：鞋带公式 + 三角剖分双重校验
- 坐标转换模块：XYZ/BLH/NEU 坐标互转，支持 7 种椭球参数
- 滑坡监测模块：位移速度、应变计算、异常预警
- PyQt6 图形用户界面
- 统一的数据导入导出功能
- 完整的日志系统
- 矩阵计算引擎（支持病态矩阵处理）
- 椭球参数配置文件

### Features

- 自动文件编码检测（UTF-8, GBK, GB2312 等）
- 自动分隔符识别（空格, Tab, 逗号）
- Markdown 报告导出
- CSV 数据导出
- PNG/PDF 图形导出
- 调试管理器

### Documentation

- README.md 项目说明
- 导入文件格式要求.md 数据格式文档
- DSP.md 系统设计文档

---

## Future Releases

敬请期待后续版本的更新！
