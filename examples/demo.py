"""综合视觉识别系统 —— 调用示例

用法:
    python demo.py              # 默认尝试摄像头 0；无摄像头则回退到 test_circle.png
    python demo.py 1            # 使用摄像头 1
    python demo.py video.mp4    # 识别视频文件
    python demo.py test.jpg     # 识别单张图片

退出:  按 q 键
"""

import sys
import os
import time

import cv2

# 确保能找到 src 模块（从项目根目录运行）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.综合视觉识别系统 import VisionSystem


def main():
    # 解析图像来源
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        src = int(arg) if arg.isdigit() else arg
    else:
        src = 0

    # 打开来源；摄像头不可用时回退到内置测试图片
    try:
        vs = VisionSystem(src=src)
    except RuntimeError as e:
        if src == 0:
            print(f"[警告] 摄像头不可用：{e}")
            print("[信息] 回退到内置测试图片 test_circle.png")
            vs = VisionSystem(src=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "test_circle.png"))
        else:
            raise

    try:
        while True:
            frame = vs.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            # 取预处理线程产出的二值图做轮廓分析
            with vs.processed_lock:
                processed = vs.processed

            if processed is not None:
                # 1) 优先检测最大圆形轮廓
                (cx, cy), contour = vs.detect_main_contour(processed, require_circle=True)
                if contour is not None:
                    ctype = vs.detect_circle_type(contour)   # solid_circle / hollow_circle
                    color = vs.detect_color(contour, frame=frame)
                    label = f"{ctype} / {color} ({cx},{cy})"
                    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                    cv2.putText(frame, label, (cx - 80, cy - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    print(f"[圆]   类型={ctype}  颜色={color}  中心=({cx},{cy})")
                else:
                    # 2) 没有圆则检测最大轮廓的形状
                    (cx, cy), contour = vs.detect_main_contour(processed)
                    if contour is not None:
                        shape = vs.detect_shape(contour)
                        color = vs.detect_color(contour, frame=frame)
                        cv2.drawContours(frame, [contour], -1, (255, 0, 0), 2)
                        cv2.putText(frame, f"{shape}/{color}", (cx - 50, cy - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                        print(f"[形状] {shape}  颜色={color}  中心=({cx},{cy})")

            cv2.imshow("VisionSystem Demo", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("收到 q，退出")
                break
    finally:
        vs.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
