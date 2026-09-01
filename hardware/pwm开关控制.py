import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

INA_PIN = 21   # A 接 BCM 21
INB_PIN = 20   # B 接 BCM 20

GPIO.setup(INA_PIN, GPIO.OUT)
GPIO.setup(INB_PIN, GPIO.OUT)

pwm_ina = GPIO.PWM(INA_PIN, 1000)
pwm_inb = GPIO.PWM(INB_PIN, 1000)
pwm_ina.start(0)
pwm_inb.start(0)

def fan_forward(speed=80):
    pwm_ina.ChangeDutyCycle(speed)
    pwm_inb.ChangeDutyCycle(0)
    print("🔄 正转，速度: {}%".format(speed))   # 这里改了

def fan_reverse(speed=80):
    pwm_ina.ChangeDutyCycle(0)
    pwm_inb.ChangeDutyCycle(speed)
    print("🔄 反转，速度: {}%".format(speed))   # 这里改了

def fan_stop():
    pwm_ina.ChangeDutyCycle(0)
    pwm_inb.ChangeDutyCycle(0)
    print("⏹️ 停止")

try:
    while True:
        fan_forward(80)
        time.sleep(2)
        fan_stop()
        time.sleep(1)
        fan_reverse(80)
        time.sleep(2)
        fan_stop()
        time.sleep(1)
except KeyboardInterrupt:
    pass

pwm_ina.stop()
pwm_inb.stop()
GPIO.cleanup()