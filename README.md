<div align="center">

# ZCodeProject — 综合视觉识别系统

> OpenCV · 形状识别 · 颜色检测 · 树莓派 GPIO 控制

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.7+-5C3EE8?logo=opencv)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-blue)](#许可证)

[快速开始](#-快速开始) · [功能特性](#-功能特性) · [项目结构](#-项目结构) · [API 文档](#-api-使用) · [硬件控制](#-硬件控制)

</div>

---

## 📋 概述

**ZCodeProject** 是一个面向树莓派的综合视觉识别工程，核心由 `VisionSystem` 类实现，支持实时形状识别、颜色检测、圆形分类，并配套 GPIO 硬件控制脚本（风扇 PWM、蜂鸣器）。

适用场景：竞赛视觉任务、创客项目、树莓派视觉教学。

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🔷 **形状识别** | 三角形、正方形/长方形、五边形、多边形、圆、空心圆 |
| 🎨 **颜色检测** | HSV/BGR 双模式，识别红/橙/黄/绿/青/蓝/紫/粉/白/灰/黑 11 种颜色 |
| ⭕ **圆形专项** | 基于圆形度公式 `4πA/P²` 区分实心圆与空心圆 |
| 📹 **多源输入** | 摄像头、视频文件、单张图片，无摄像头时自动回退内置测试图 |
| ⚡ **双线程架构** | 采集线程 + 预处理线程，帧锁保证线程安全 |
| 🔌 **GPIO 控制** | 树莓派风扇 PWM 正反转/调速、蜂鸣器通断 |

---

## 📦 项目结构

```
ZCodeProject/
├── 📁 src/                     # 核心模块
│   └── 综合视觉识别系统.py      # VisionSystem 类（形状/颜色/圆形识别）
│
├── 📁 examples/                # 示例脚本
│   ├── demo.py                 # 调用示例（摄像头/视频/图片）
│   └── make_sample.py          # 测试图生成脚本
│
├── 📁 hardware/                # 硬件控制
│   ├── pwm开关控制.py           # 树莓派风扇 PWM 控制（INA=21, INB=20）
│   └── 蜂鸣器通断.py            # 树莓派蜂鸣器控制（BCM 14）
│
├── 📁 assets/                  # 资源文件
│   └── test_circle.png         # 内置测试图片（无需摄像头即可验证）
│
├── 📄 requirements.txt         # Python 依赖
├── 📄 .gitignore               # Git 忽略规则
└── 📄 README.md                # 项目说明
```

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

> `requirements.txt` 锁定 `opencv-python<5` 和 `numpy<2`，兼容 Python 3.8。

### 运行示例

> ⚠️ **从项目根目录运行**

```bash
# 使用摄像头（默认索引 0）
python examples/demo.py 0

# 使用视频文件
python examples/demo.py video.mp4

# 使用图片（摄像头不可用时自动回退到 assets/test_circle.png）
python examples/demo.py
```

运行后实时窗口显示识别结果，按 `q` 退出。

### 生成测试图

```bash
python examples/make_sample.py
# 生成 assets/test_circle.png（含实心红圆、蓝色方块、紫色三角、暗绿方块）
```

---

## 🔧 API 使用

```python
from src.综合视觉识别系统 import VisionSystem

vs = VisionSystem()
vs.open_camera(0)  # 打开摄像头

while True:
    contour = vs.detect_main_contour(require_circle=True)
    if contour:
        shape = vs.detect_shape(contour)
        circle_type = vs.detect_circle_type(contour)
        color = vs.detect_color(contour)
        print(f"形状: {shape}, 圆类型: {circle_type}, 颜色: {color}")

vs.release()
```

---

## 📡 硬件控制

### 风扇 PWM 控制

```python
from hardware.pwm开关控制 import fan_forward, fan_reverse, fan_stop

fan_forward(80)   # 正转 80% 占空比
fan_stop()         # 停止
fan_reverse(50)    # 反转 50%
```

### 蜂鸣器控制

```python
from hardware.蜂鸣器通断 import buzzer_on, buzzer_off

buzzer_on()   # 响
buzzer_off()  # 停
```

---

## 🛠 技术栈

| 技术 | 用途 |
|------|------|
| OpenCV 4.7+ | 图像采集、预处理、轮廓/形状/颜色识别 |
| NumPy 1.21+ | 数组运算、圆形度计算 |
| threading | 双线程并发（采集 + 预处理） |
| RPi.GPIO | 树莓派硬件控制（仅树莓派环境可用） |

---

## ❓ 常见问题

<details>
<summary><b>Q: 提示找不到 src 模块？</b></summary>

请确保从**项目根目录**运行脚本：
```bash
# ✅ 正确
cd ZCodeProject
python examples/demo.py

# ❌ 错误（进入 examples 目录运行）
cd examples
python demo.py
```
</details>

<details>
<summary><b>Q: 摄像头无法打开？</b></summary>

脚本会自动回退到内置测试图 `assets/test_circle.png`，无需摄像头即可验证识别功能。
</details>

<details>
<summary><b>Q: RPi.GPIO 导入失败？</b></summary>

`RPi.GPIO` 仅在树莓派环境可用。在 PC 上运行时，硬件控制脚本会导入失败，但视觉识别功能不受影响。
</details>

---

## 📄 许可证

MIT License

---

<div align="center">

由 [LONEFORME](https://github.com/LONEFORME) 维护

</div>
