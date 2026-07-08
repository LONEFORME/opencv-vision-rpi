"""生成内置测试图片 test_circle.png

图片含: 实心红圆、蓝色方块、紫色三角、暗绿色方块，
用于在没有摄像头时验证视觉识别流程（形状 / 圆 / 颜色）。

注意: 默认二值化阈值为 60（THRESH_BINARY_INV，找暗物体），
因此这里的前景颜色都取灰度 < 60 的值，确保能被正确提取。

运行:  python make_sample.py
"""

import cv2
import numpy as np

W, H = 640, 480
img = np.full((H, W, 3), 255, dtype=np.uint8)  # 白底

# 实心红圆（暗红，灰度≈48 < 60，可提取）
cv2.circle(img, (160, 160), 60, (0, 0, 160), -1)
# 蓝色方块（灰度≈29）
cv2.rectangle(img, (120, 320), (240, 440), (255, 0, 0), -1)
# 紫色三角（灰度≈53）
pts = np.array([[440, 440], [500, 320], [560, 440]], np.int32)
cv2.fillPoly(img, [pts], (128, 0, 128))
# 暗绿色方块（灰度≈59 < 60）
cv2.rectangle(img, (380, 120), (500, 240), (0, 100, 0), -1)

cv2.imwrite("test_circle.png", img)
print("已生成 test_circle.png")
