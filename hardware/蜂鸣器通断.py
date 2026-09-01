import RPi.GPIO as GPIO
import time

# 设置 GPIO 编码方式
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 定义蜂鸣器引脚（你可以改成任意BCM引脚，比如 12、17、22 等）
BUZZER_PIN = 14

# 设置为输出模式
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def buzzer_on():
    """打开蜂鸣器（输出高电平）"""
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    print("🔊 蜂鸣器已打开")

def buzzer_off():
    """关闭蜂鸣器（输出低电平）"""
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    print("🔇 蜂鸣器已关闭")

# 示例：响 1 秒，停 1 秒，循环 3 次
try:
    for _ in range(3):
        buzzer_on()
        time.sleep(1)
        buzzer_off()
        time.sleep(1)
    print("演示结束")
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()   # 释放所有GPIO资源