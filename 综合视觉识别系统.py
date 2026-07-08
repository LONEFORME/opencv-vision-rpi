import cv2
import threading
import time
import numpy as np


def is_circle(contour):
    circularity_thresh = 0.7
    min_area = 500
    max_area = 100000
    # 计算轮廓面积和周长
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)

    if perimeter == 0:
        return False

    # 计算圆形度: 4*pi*A/P^2 (完美圆形为1)
    circularity = 4 * np.pi * area / (perimeter ** 2)

    # 圆形度接近1且面积在合理范围内
    return circularity > circularity_thresh and min_area < area < max_area


class VisionSystem:
    def __init__(self, src=0):
        self.shape = None
        self.frame = None
        self.centers = []
        self.frame_lock = threading.Lock()  # 帧数据锁
        self.camera_open = False  # 摄像头状态标志
        self.running = False
        self.cap = None
        self.src = src  # 保存摄像头设备号/路径

        self._init_camera(src)

        # 启动摄像头和处理线程
        self.capture_thread = threading.Thread(target=self._capture, daemon=True)
        self.preprocess_thread = threading.Thread(target=self.preprocess_frame, daemon=True)

        self.capture_thread.start()
        self.preprocess_thread.start()

        self.blur_kernel_size = 7  # 高斯模糊核大小
        self.threshold_value = 60  # 二值化阈值
        self.min_contour_area = 3000  # 最小轮廓面积
        self.max_contour_area = 100000  # 最大轮廓面积
        self.dilate_iterations = 1  # 膨胀迭代次数
        self.erode_iterations = 1  # 腐蚀迭代次数
        self.circularity_threshold = 0.7  # 圆形度阈值
        self.hollow_ratio_threshold = 0.5  # 空心圆面积比阈值

        self.last_contour = None
        self.last_processed = None
        self.processed = None  # 预处理后的二值图（线程安全由 frame_lock 保护）
        self.processed_lock = threading.Lock()  # 预处理结果锁

        # 等待第一帧数据
        while self.frame is None and self.running:
            time.sleep(0.1)

    #初始化摄像头，默认src=0
    def _init_camera(self, src=0):
        """内部方法：初始化摄像头"""
        self.cap = cv2.VideoCapture(self.src)
        if not self.cap.isOpened():
            raise RuntimeError("无法打开摄像头:", self.src)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        self.cap.set(3, 320)
        self.cap.set(4, 240)
        self.camera_open = True
        self.running = True

    #确认摄像头是否打开
    def is_camera_open(self):
        """检查摄像头是否正在运行"""
        return self.camera_open

    #关闭摄像头
    def close_camera(self):
        """关闭当前摄像头"""
        if self.camera_open:
            self.camera_open = False
            self.running = False
            if self.cap:
                self.cap.release()
                self.cap = None
            print("摄像头:", self.src)
            print("已关闭")

    #重开摄像头
    def reopen_camera(self, src=0):
        """关闭当前摄像头并重新打开指定摄像头"""
        self.close_camera()
        self.src = src
        self._init_camera(src)
        print("摄像头: ", self.src, "已重新开启")

        # 重启线程
        self.capture_thread = threading.Thread(target=self._capture, daemon=True)
        self.preprocess_thread = threading.Thread(target=self.preprocess_frame, daemon=True)

        self.capture_thread.start()
        self.preprocess_thread.start()

        # 等待第一帧
        while self.frame is None and self.running:
            time.sleep(0.1)

    #设置图像处理参数
    # def set_params(self, blur_size=5, threshold=60, min_area=500, max_area=20000,
    #                dilate=1, erode=1):
    #     """设置轮廓检测参数"""
    #     self.blur_kernel_size = max(3, blur_size)  # 确保最小为3且为奇数
    #     if self.blur_kernel_size % 2 == 0:
    #         self.blur_kernel_size += 1
    #
    #     self.threshold_value = max(1, min(255, threshold))
    #     self.min_contour_area = max(1, min_area)
    #     self.max_contour_area = max(min_area, max_area)
    #     self.dilate_iterations = max(0, dilate)
    #     self.erode_iterations = max(0, erode)

    #采集图像
    # 捕获线程
    def _capture(self):
        """摄像头捕获线程"""
        while self.running:
            if self.camera_open:
                ret, frame = self.cap.read()
                if ret:
                    with self.frame_lock:
                        self.frame = frame
                else:
                    time.sleep(0.1)
            else:
                time.sleep(0.1)

    # 获取图像
    def get_frame(self):
        """获取当前帧（线程安全）"""
        with self.frame_lock:
            return self.frame.copy() if self.frame is not None else None

    # 获取图像的中心点
    def get_image_center(self):
        frame = self.get_frame()
        if frame is None:
            return None
        height, width = frame.shape[:2]  # 获取图像高度和宽度
        center_x = width // 2
        center_y = height // 2
        return center_x, center_y

    #处理图像
    def preprocess_frame(self):
        while self.running:
            if self.frame is not None:
                # 处理帧数据
                with self.frame_lock:
                    frame = self.frame.copy()
                # 图像处理流水线
                """图像预处理流程"""

                # 转换为灰度图
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # 高斯模糊
                blurred = cv2.GaussianBlur(gray, (self.blur_kernel_size, self.blur_kernel_size), 0)
                # 二值化
                _, thresh = cv2.threshold(blurred, self.threshold_value, 255, cv2.THRESH_BINARY_INV)
                # 形态学核
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                # 先膨胀后腐蚀（闭运算）
                if self.dilate_iterations > 0:
                    thresh = cv2.dilate(thresh, kernel, iterations=self.dilate_iterations)
                if self.erode_iterations > 0:
                    thresh = cv2.erode(thresh, kernel, iterations=self.erode_iterations)
                # 存回实例供 detect_main_contour 使用；注意不能 return，否则线程只跑一帧就退出
                with self.processed_lock:
                    self.processed = thresh
            else:
                time.sleep(0.01)

    #找出最大轮廓（可选：仅保留圆形轮廓）
    def detect_main_contour(self, processed_frame, require_circle=False):
        """检测主轮廓并返回中心坐标与轮廓
        :param processed_frame: 二值化后的图像
        :param require_circle: 为 True 时只接受圆形度达标的轮廓
        """
        # 查找轮廓
        result = cv2.findContours(processed_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 函数检测轮廓，简化轮廓
        contours = result[0] if len(result) == 2 else result[1]

        # 过滤掉太小或太大的轮廓
        filtered_contours = [
            cnt for cnt in contours
            if self.min_contour_area < cv2.contourArea(cnt) < self.max_contour_area
        ]

        if require_circle:
            filtered_contours = [cnt for cnt in filtered_contours if is_circle(cnt)]

        if len(filtered_contours) > 0:
            # 找出最大轮廓
            main_contour = max(filtered_contours, key=cv2.contourArea)

            # 计算轮廓的矩和中心
            m = cv2.moments(main_contour)
            if m["m00"] != 0:
                c_x = int(m["m10"] / m["m00"])
                c_y = int(m["m01"] / m["m00"])
                return (c_x, c_y), main_contour
        return (0, 0), None

    #检测图像形状
    @staticmethod
    def detect_shape(contour, epsilon_factor=0.04):
        """
        检测轮廓的形状
        :param contour: 输入轮廓
        :param epsilon_factor: 近似轮廓的精度因子(越小越精确)
        """
        if contour is None or len(contour) < 3:
            return None

        # 计算轮廓周长和近似多边形
        perimeter = cv2.arcLength(contour, True)
        epsilon = epsilon_factor * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # 根据顶点数量判断形状
        vertices = len(approx)
        shape = None

        if vertices == 3:
            shape = "三角形"
        elif vertices == 4:
            # 区分矩形和正方形
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h
            shape = "正方形" if 0.95 <= aspect_ratio <= 1.05 else "长方形"
        elif vertices == 5:
            shape = "五边形"
        elif vertices == 6:
            shape = "多边形"
        else:
            # 可能是圆形或椭圆形
            area = cv2.contourArea(contour)
            (x, y), radius = cv2.minEnclosingCircle(contour)
            circle_area = np.pi * (radius ** 2)

            # 如果实际面积与最小外接圆面积相近，则认为是圆形
            if 0.9 <= (area / circle_area) <= 1.0:
                shape = "圆"
            else:
                shape = "空心圆"

        return shape

    #检测圆的类型
    def detect_circle_type(self, contour):
        if contour is None or len(contour) < 5:
            return None
        # 计算圆形度
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            return None
        circularity = 4 * np.pi * area / (perimeter ** 2)
        if circularity < self.circularity_threshold:
            return None  # 不是圆形
        # 计算最小外接圆
        (x, y), radius = cv2.minEnclosingCircle(contour)
        enclosing_area = np.pi * (radius ** 2)
        if enclosing_area == 0:
            return None
        area_ratio = area / enclosing_area
        # 判断实心/空心
        if area_ratio > self.hollow_ratio_threshold:
            return "solid_circle"
        else:
            return "hollow_circle"

    def detect_circles(self, frame=None, draw_result=True):
        if frame is None:
            with self.frame_lock:
                if self.frame is None:
                    return None, []
                frame = self.frame.copy()

        # 预处理（阈值使用类参数 self.threshold_value，保持与其他函数一致）
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        _, binary = cv2.threshold(blurred, self.threshold_value, 255, cv2.THRESH_BINARY_INV)
        result = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = result[0] if len(result) == 2 else result[1]
        hierarchy = result[1] if len(result) == 3 else (result[2] if len(result) == 3 else None)
        if len(result) == 2:
            hierarchy = None
        else:
            hierarchy = result[2] if len(result) == 3 else result[1]

        if hierarchy is not None:
            hierarchy = hierarchy[0]
            for i, contour in enumerate(contours):
                # 检查是否是圆形
                if not is_circle(contour):
                    continue

                # 获取轮廓的中心点
                m = cv2.moments(contour)
                if m["m00"] != 0:
                    c_x = int(m["m10"] / m["m00"])
                    c_y = int(m["m01"] / m["m00"])
                else:
                    c_x, c_y = 0, 0

                if hierarchy[i][3] == -1:
                    label = ""
                    color = (0, 0, 0)

                    if hierarchy[i][2] != -1:
                        # 有子轮廓 -> 空心圆
                        label = "Hollow"
                        color = (0, 255, 0)  # 绿色
                    else:
                        # 没有子轮廓 -> 实心圆
                        label = "Solid"
                        color = (0, 0, 255)  # 红色

                    cv2.drawContours(frame, [contour], -1, color, 3)
                    cv2.putText(frame, label, (c_x - 40, c_y), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow('Live Detection', frame)
        cv2.imshow('Binary Image', binary)
        cv2.waitKey(1)  # 必须调用，否则窗口不刷新/程序卡死

    #检测形状的颜色
    def detect_color(self, contour, frame=None, color_space="hsv"):

        # :param contour: 输入轮廓（必须是np.ndarray格式，形状为(N,1,2)）
        # :param frame: 原始帧(如果None则使用当前帧)
        # :param color_space: 使用的颜色空间("hsv"或"bgr")

        if contour is None or len(contour) < 3:
            return None

        contour = np.asarray(contour, dtype=np.int32).reshape((-1, 1, 2))

        if frame is None:
            with self.frame_lock:
                if self.frame is None:
                    return None
                frame = self.frame.copy()

        # 创建掩码
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)

        # 计算掩码区域的均值颜色
        mean_color_bgr = cv2.mean(frame, mask=mask)[:3]

        if color_space.lower() == "hsv":

            mean_color_bgr = np.uint8([[mean_color_bgr]])
            hsv_color = cv2.cvtColor(mean_color_bgr, cv2.COLOR_BGR2HSV)[0][0]
            hue, sat, val = hsv_color

            # 考虑饱和度和亮度的影响
            if sat < 40 or val < 40:  # 饱和度或亮度太低
                return "white" if val > 200 else "gray" if val > 50 else "black"

            # 根据色调判断颜色（OpenCV中Hue范围是0-180）
            if hue < 5 or hue > 175:
                return "red"
            elif 5 <= hue < 15:
                return "orange"
            elif 15 <= hue < 33:
                return "yellow"
            elif 33 <= hue < 75:
                return "green"
            elif 75 <= hue < 105:
                return "cyan"
            elif 105 <= hue < 135:
                return "blue"
            elif 135 <= hue < 155:
                return "purple"
            elif 155 <= hue < 175:
                return "pink"
            else:
                return "unknown"
        else:
            # BGR颜色空间判断
            b, g, r = mean_color_bgr
            max_val = max(r, g, b)

            if max_val < 30:  # 接近黑色
                return "black"
            elif abs(r - g) < 30 and abs(r - b) < 30 and abs(g - b) < 30:  # 灰度色
                return "white" if max_val > 200 else "gray"

            # 彩色判断
            if r > g * 1.4 and r > b * 1.4:
                return "red"
            elif g > r * 1.4 and g > b * 1.4:
                return "green"
            elif b > r * 1.4 and b > g * 1.4:
                return "blue"
            elif r > g * 1.2 and g > b * 1.2:
                return "yellow"
            elif b > g * 1.2 and g > r * 1.2:
                return "cyan"
            else:
                return "unknown"

    #结束图像获取
    def release(self):
        """完全释放资源（停止所有线程和摄像头）"""
        self.running = False
        self.close_camera()

        # 等待线程结束
        for thread in [self.capture_thread, self.preprocess_thread]:
            if thread.is_alive():
                thread.join()

        print("所有资源已释放")
