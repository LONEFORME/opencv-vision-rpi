<div align="center">

# opencv-vision-rpi — 综合计算机视觉识别系统

> OpenCV · 11 色自适应检测 · 几何轮廓分类 · 实心/空心圆判定 · 双线程并发架构

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.7+-5C3EE8?logo=opencv)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](#-许可证)

[快速开始](#-快速开始) · [功能特性](#-功能特性) · [项目结构](#-项目结构) · [API 文档](#-api-使用) · [技术栈](#-技术栈)

</div>

---

## 📋 概述

**opencv-vision-rpi** 是一个基于 OpenCV 的高性能综合计算机视觉识别工程，核心由 `VisionSystem` 类封装实现。

系统采用多线程异步解耦架构，支持在摄像头、视频文件与单张图片输入源下，高帧率实时执行 **11 种颜色自适应提取**、**多边形几何形状分类**以及基于数学圆形度指标的**实心圆与空心圆环严密区分**。

适用场景：智能车/机器人竞赛视觉任务、目标追踪靶标检测、工科创客实验与嵌入式计算机视觉教学。

---

## ✨ 功能特性

| 功能模块 | 算法原理与技术特性 | 应用场景 |
| :--- | :--- | :--- |
| 🎨 **11 色自适应检测** | HSV 与 BGR 双色彩空间动态自适应判定，覆盖红/橙/黄/绿/青/蓝/紫/粉/白/灰/黑 | 复杂光照环境下的色块识别与标志物过滤 |
| 🔷 **几何形状识别** | 多边形逼近算法（`cv2.approxPolyDP`），精准分类三角形（3）、矩形/方块（4）、五边形（5）、多边形（>5） | 场地标志、几何图形识别 |
| ⭕ **圆形专项度量** | 计算严格数学圆形度 $C = \frac{4\pi A}{P^2}$ 并结合轮廓内外拓扑，区分**实心圆**与**空心圆环** | 电赛靶心、圆环穿越与管道口检测 |
| ⚡ **双线程流水线架构** | 采集线程与预处理/二值化线程分离并发，互斥帧锁（`threading.Lock`）保证无死锁与极低延迟 | 树莓派 / 嵌入式开发板上榨干多核性能 |
| 📹 **多源无缝回退** | 支持 USB 摄像头（0, 1）、MP4 视频文件与单张图片；无相机时自动回退至内置测试图 | 离线算法验证与持续集成 |

---

## 📦 项目结构

```text
opencv-vision-rpi/
├── 📁 src/                     # 核心算法模块
│   └── 综合视觉识别系统.py      # VisionSystem 核心类（颜色/形状/圆形分类器与双线程流水线）
│
├── 📁 examples/                # 示例与调用脚本
│   ├── demo.py                 # 多源实时运行 Demo（支持相机、视频、图片与自动回退）
│   └── make_sample.py          # 纯代码离线生成标准测试样本图脚本
│
├── 📁 assets/                  # 静态资源
│   └── test_circle.png         # 内置多色几何测试图（红圆、蓝方、紫三角、绿方）
│
├── 📄 requirements.txt         # 核心 Python 依赖（OpenCV, NumPy）
├── 📄 .gitignore               # Git 忽略规则
└── 📄 README.md                # 项目全景说明
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

> `requirements.txt` 兼容 Python 3.8 ~ 3.12，无需特殊系统级额外驱动。

### 2. 运行实时识别演示

> ⚠️ **请在项目根目录下运行脚本**

```bash
# 模式 A：默认自动检测摄像头 0（无摄像头自动优雅回退到内置测试图）
python examples/demo.py

# 模式 B：指定特定摄像头设备号（如 USB 摄像头 1）
python examples/demo.py 1

# 模式 C：识别离线视频文件
python examples/demo.py test_video.mp4

# 模式 D：识别指定静态图片
python examples/demo.py my_target.jpg
```

运行后将弹出实时可视化窗口，实时绘制目标轮廓、中心点坐标与标签，按 `q` 键退出。

### 3. 生成标准测试图像

无需物理摄像头即可离线验证算法：
```bash
python examples/make_sample.py
# 将在 assets/ 目录下自动生成包含多种颜色与形状的标准测试图 test_circle.png
```

---

## 🔧 API 使用指南

可在您的第三方机器人主控或上位机程序中直接调用 `VisionSystem`：

```python
from src.综合视觉识别系统 import VisionSystem

# 初始化视觉系统（支持摄像头索引或图片/视频路径）
vs = VisionSystem(src=0)

while True:
    frame = vs.get_frame()
    if frame is None:
        continue

    # 获取预处理线程提取的高对比二值图
    with vs.processed_lock:
        processed = vs.processed

    if processed is not None:
        # 1. 优先提取主圆形轮廓
        (cx, cy), contour = vs.detect_main_contour(processed, require_circle=True)
        if contour is not None:
            circle_type = vs.detect_circle_type(contour)  # solid_circle / hollow_circle
            color = vs.detect_color(contour, frame=frame)
            print(f"[锁定目标] 类型: {circle_type}, 颜色: {color}, 目标中心点: ({cx}, {cy})")
        else:
            # 2. 提取常规几何形状轮廓
            (cx, cy), contour = vs.detect_main_contour(processed)
            if contour is not None:
                shape = vs.detect_shape(contour)
                color = vs.detect_color(contour, frame=frame)
                print(f"[识别形状] 形状: {shape}, 颜色: {color}, 目标中心点: ({cx}, {cy})")

# 释放相机资源
vs.release()
```

---

## 🛠 技术栈

| 技术组件 | 最低版本 | 核心职责 |
| :--- | :--- | :--- |
| **OpenCV** | 4.7+ | 图像采集、高斯模糊、自适应阈值二值化、轮廓拓扑分析 |
| **NumPy** | 1.21+ | 矩阵快速运算、圆形度公式矢量计算 |
| **Threading** | Python 内置 | 多线程采集与预处理并行，避免相机 I/O 阻塞算法计算 |

---

## ❓ 常见问题 (FAQ)

<details>
<summary><b>Q: 运行 demo 提示 <code>ModuleNotFoundError: No module named 'src'</code>？</b></summary>

请确保在**项目根目录**运行脚本：
```bash
# ✅ 正确：在项目根目录下执行
cd opencv-vision-rpi
python examples/demo.py

# ❌ 错误：cd 到 examples 目录后执行
cd examples && python demo.py
```
</details>

<details>
<summary><b>Q: 现场环境没有外接 USB 摄像头，如何验证？</b></summary>

`demo.py` 内置了异常捕获机制。当检测到无可用摄像头硬件时，会自动切换为读取 `assets/test_circle.png` 示例图片，完整跑通所有色彩分类、多边形逼近与圆形度计算逻辑。
</details>

---

## 📄 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

<div align="center">
Built with ❤️ for Computer Vision & Embedded Robotics.
</div>
