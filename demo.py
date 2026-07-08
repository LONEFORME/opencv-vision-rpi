"""综合视觉识别系统 —— 调用示例

运行:  python demo.py
退出:  按 q 键

说明:
- VisionSystem 内部已用独立线程持续采集帧并做预处理；
- 本示例在主线循环里取帧，调用其 detect_* 方法做圆/形状/颜色识别并实时显示；
- src 可改为视频文件路径或 RTSP/HTTP 流地址。
"""

import time

import cv2

from 综合视觉识别系统 import VisionSystem


def main():
    # 初始化视觉系统（src=0 为默认摄像头）
    vs = VisionSystem(src=0)

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
