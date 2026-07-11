# ZCodeProject — 综合视觉识别系统

> OpenCV · 形状识别 · 颜色检测 · 树莓派 GPIO 控制

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.7+-5C3EE8?logo=opencv)](https://opencv.org/)

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
├── 综合视觉识别系统.py    # 核心模块：VisionSystem 类
├── demo.py               # 调用示例（摄像头/视频/图片）
├── make_sample.py         # 测试图生成脚本
├── test_circle.png        # 内置测试图片（无需摄像头即可验证）
├── pwm开关控制.py         # 树莓派风扇 PWM 控制（INA=21, INB=20）
├── 风扇转.py              # 同上（副本）
├── 蜂鸣器通断.py          # 树莓派蜂鸣器控制（BCM 14）
├── requirements.txt       # Python 依赖
└── .gitignore
```

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

> `requirements.txt` 锁定 `opencv-python<5` 和 `numpy<2`，兼容 Python 3.8。

### 运行示例

```bash
# 使用摄像头（默认索引 0）
python demo.py 0

# 使用视频文件
python demo.py video.mp4

# 使用图片（摄像头不可用时自动回退到 test_circle.png）
python demo.py
```

运行后实时窗口显示识别结果，按 `q` 退出。

### 生成测试图

```bash
python make_sample.py
# 生成 test_circle.png（含实心红圆、蓝色方块、紫色三角、暗绿方块）
```

---

## 🔧 API 使用

```python
from 综合视觉识别系统 import VisionSystem

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
from pwm开关控制 import fan_forward, fan_reverse, fan_stop

fan_forward(80)   # 正转 80% 占空比
fan_stop()         # 停止
fan_reverse(50)    # 反转 50%
```

### 蜂鸣器控制

```python
from 蜂鸣器通断 import buzzer_on, buzzer_off

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

## 📄 许可证

MIT License

---

<p align="center">由 <a href="https://github.com/LONEFORME">LONEFORME</a> 维护</p>
