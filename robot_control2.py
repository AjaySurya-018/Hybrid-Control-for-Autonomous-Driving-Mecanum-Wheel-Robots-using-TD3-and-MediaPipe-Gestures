import RPi.GPIO as io
import time

io.setmode(io.BCM)
io.setwarnings(False)

PWM_MAX = 100

leftMotor_DIR_pin = 22
rightMotor_DIR_pin = 23
leftMotor_PWM_pin = 17
rightMotor_PWM_pin = 18

io.setup(leftMotor_DIR_pin, io.OUT)
io.setup(rightMotor_DIR_pin, io.OUT)
io.setup(leftMotor_PWM_pin, io.OUT)
io.setup(rightMotor_PWM_pin, io.OUT)

leftMotor_PWM = io.PWM(leftMotor_PWM_pin, 1000)
rightMotor_PWM = io.PWM(rightMotor_PWM_pin, 1000)

leftMotor_PWM.start(0)
rightMotor_PWM.start(0)

leftMotorPower = 0
rightMotorPower = 0

def set_motor_left(power):
    global leftMotorPower
    if power < 0:
        io.output(leftMotor_DIR_pin, False)
        pwm = -int(PWM_MAX * power)
        if pwm > PWM_MAX:
            pwm = PWM_MAX
    elif power > 0:
        io.output(leftMotor_DIR_pin, True)
        pwm = int(PWM_MAX * power)
        if pwm > PWM_MAX:
            pwm = PWM_MAX
    else:
        io.output(leftMotor_DIR_pin, False)
        pwm = 0
    leftMotorPower = pwm
    leftMotor_PWM.ChangeDutyCycle(pwm)

def set_motor_right(power):
    global rightMotorPower
    if power < 0:
        io.output(rightMotor_DIR_pin, True)
        pwm = -int(PWM_MAX * power)
        if pwm > PWM_MAX:
            pwm = PWM_MAX
    elif power > 0:
        io.output(rightMotor_DIR_pin, False)
        pwm = int(PWM_MAX * power)
        if pwm > PWM_MAX:
            pwm = PWM_MAX
    else:
        io.output(rightMotor_DIR_pin, False)
        pwm = 0
    rightMotorPower = pwm
    rightMotor_PWM.ChangeDutyCycle(pwm)

# Exiting code
def exit():
    io.output(leftMotor_DIR_pin, False)
    io.output(rightMotor_DIR_pin, False)
    io.cleanup()
    
# Main code
while True:
    # Simulating gesture recognition inputs
    gesture = input("Enter recognized gesture: ")

    if gesture == "stop":
        set_motor_left(0)
        set_motor_right(0)
    elif gesture == "fist":
        set_motor_left(-0.5)
        set_motor_right(-0.5)
    elif gesture == "thumbs up":
        set_motor_left(0.5)
        set_motor_right(-0.5)
    elif gesture == "thumbs down":
        set_motor_left(-0.5)
        set_motor_right(0.5)
    elif gesture == "call me":
        leftMotorPower += 10
        rightMotorPower += 10
        set_motor_left(leftMotorPower)
        set_motor_right(rightMotorPower)
    elif gesture == "peace":
        leftMotorPower -= 10
        rightMotorPower -= 10
        set_motor_left(leftMotorPower)
        set_motor_right(rightMotorPower)
    else:
        print("Invalid gesture")
