import sys
import tty
import termios
import os
import MDD10A as HBridge
import time
import RPi.GPIO as io
import cv2 as cv
import numpy as np
import math

cap = cv.VideoCapture(0)    

# Motor control pins
leftMotor_PWM_pin = 17
rightMotor_PWM_pin = 18
leftMotor_DIR_pin = 22  # Define the DIR pin for the left motor
rightMotor_DIR_pin = 23  # Define the DIR pin for the right motor

# Set up motor control pins
io.setmode(io.BCM)
io.setup(leftMotor_PWM_pin, io.OUT)
io.setup(rightMotor_PWM_pin, io.OUT)
io.setup(leftMotor_DIR_pin, io.OUT)  # Set the left motor DIR pin as output
io.setup(rightMotor_DIR_pin, io.OUT)  # Set the right motor DIR pin as output

# Maximum PWM value
PWM_MAX = 100

# Initialize PWM objects for left and right motors
leftMotorPWM = io.PWM(leftMotor_PWM_pin, 1000)
rightMotorPWM = io.PWM(rightMotor_PWM_pin, 1000)

# Start PWM with 0 duty cycle
leftMotorPWM.start(0)
rightMotorPWM.start(0)

# Initialize motor powers
leftMotorPower = 0
rightMotorPower = 0

# Function to get keyboard input
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Function to print screen
def printscreen():
    os.system('clear')
    print("w/s: direction")
    print("a/d: steering")
    print("q: stops the motors")
    print("x: exit")
    print("========== Speed Control ==========")
    print("left motor:  ", leftMotorPower)
    print("right motor: ", rightMotorPower)

# Function to set left motor power
def setMotorLeft(power):
    global leftMotorPower
    if power < 0:
        io.output(leftMotor_DIR_pin, False)  # Set the left motor direction to forward
        pwm = -int(PWM_MAX * power)
        if pwm > PWM_MAX:
            pwm = PWM_MAX
    elif power > 0:
        io.output(leftMotor_DIR_pin, True)  # Set the left motor direction to reverse
        pwm = int(PWM_MAX * power)
        if pwm > PWM_MAX:
            pwm = PWM_MAX
    else:
        io.output(leftMotor_DIR_pin, False)  # Set the left motor direction to forward (stop)
        pwm = 0
    leftMotorPower = pwm
    leftMotorPWM.ChangeDutyCycle(pwm)

# Function to set right motor power
def setMotorRight(power):
    global rightMotorPower
    if power < 0:
        io.output(rightMotor_DIR_pin, True)  # Set the right motor direction to forward
        pwm = -int(PWM_MAX * power)
        if pwm > PWM_MAX:
            pwm = PWM_MAX
    elif power > 0:
        io.output(rightMotor_DIR_pin, False)  # Set the right motor direction to reverse
        pwm = int(PWM_MAX * power)
        if pwm > PWM_MAX:
            pwm = PWM_MAX
    else:
        io.output(rightMotor_DIR_pin, False)  # Set the right motor direction to forward (stop)
        pwm = 0
    rightMotorPower = pwm
    rightMotorPWM.ChangeDutyCycle(pwm)

# Function to exit and clean up
def exit():
    io.output(leftMotor_DIR_pin, False)
    io.output(rightMotor_DIR_pin, False)
    io.cleanup()

def count_finger_defects():
    _, img = cap.read()
    cv.rectangle(img, (300, 300), (100, 100), (0, 255, 0), 0)
    crop_img = img[100:300, 100:300]
    grey = cv.cvtColor(crop_img, cv.COLOR_BGR2GRAY)
    value = (35, 35)
    blurred_ = cv.GaussianBlur(grey, value, 0)
    _, thresholded = cv.threshold(blurred_, 127, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

    contours, _ = cv.findContours(thresholded.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    count1 = max(contours, key=lambda x: cv.contourArea(x))
    x, y, w, h = cv.boundingRect(count1)
    cv.rectangle(crop_img, (x, y), (x + w, y + h), (0, 0, 255), 0)
    hull = cv.convexHull(count1)
    drawing = np.zeros(crop_img.shape, np.uint8)
    cv.drawContours(drawing, [count1], 0, (0, 255, 0), 0)
    cv.drawContours(drawing, [hull], 0, (0, 0, 255), 0)
    hull = cv.convexHull(count1, returnPoints=False)
    defects = cv.convexityDefects(count1, hull)

    count_defects = 0
    cv.drawContours(thresholded, contours, -1, (0, 255, 0), 3)

    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(count1[s][0])
        end = tuple(count1[e][0])
        far = tuple(count1[f][0])
        a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

        if angle <= 90:
            count_defects += 1
            cv.circle(crop_img, far, 1, [0, 0, 255], -1)

        cv.line(crop_img, start, end, [0, 255, 0], 2)

    if count_defects == 1:
        cv.putText(img, "2 fingers", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255))
    elif count_defects == 2:
        str = "3 fingers"
        cv.putText(img, str, (5, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
    elif count_defects == 3:
        cv.putText(img, "4 fingers", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255))
    elif count_defects == 4:
        cv.putText(img, "5 fingers", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255))
    elif count_defects == 0:
        cv.putText(img, "one", (50, 50), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255))

    cv.imshow('main window', img)
    all_img = np.hstack((drawing, crop_img))
    cv.imshow('Contours', all_img)

    return count_defects

# Function to recognize gestures based on the number of fingers
def recognizeGesture(finger_count):
    if finger_count == 1:
        return "1 finger"
    elif finger_count == 2:
        return "2 fingers"
    elif finger_count == 3:
        return "3 fingers"
    elif finger_count == 4:
        return "4 fingers"
    elif finger_count == 5:
        return "5 fingers"
    else:
        return "Unknown gesture"
    
# Main function for controlling the robot based on gesture recognition
def main():
    print("Press 'x' to exit")
    while True:
        char = getch()
        if char == "x":
            exit()
            print("Program Ended")
            break
        finger_count = count_finger_defects()  # Simulate finger counting (Replace with your actual logic)
        gesture = recognizeGesture(finger_count)
        print("Recognized Gesture:", gesture)

        if gesture == "1 finger":
            # Move forward by adjusting speeds and direction
            setMotorLeft(0.5)  # Adjust the speed as needed
            setMotorRight(0.5)  # Adjust the speed as needed
        elif gesture == "2 fingers":
            # Stop by gradually decreasing speed and move backward by adjusting speeds and direction
            setMotorLeft(0)  # Stop left motor
            setMotorRight(0)  # Stop right motor
            time.sleep(1)  # Wait for a brief moment
            setMotorLeft(-0.5)  # Adjust the speed and direction as needed for backward movement
            setMotorRight(-0.5)  # Adjust the speed and direction as needed for backward movement
        elif gesture == "3 fingers":
            # Move rightwards by adjusting speeds and direction
            setMotorLeft(0.5)  # Adjust the speed and direction as needed for rightward movement
            setMotorRight(-0.5)  # Adjust the speed and direction as needed for rightward movement
        elif gesture == "4 fingers":
            # Move leftwards by adjusting speeds and direction
            setMotorLeft(-0.5)  # Adjust the speed and direction as needed for leftward movement
            setMotorRight(0.5)  # Adjust the speed and direction as needed for leftward movement
        elif gesture == "5 fingers":
            # Increase the speed of the wheels to make the robot move fast gradually
            setMotorLeft(1)  # Adjust the speed as needed
            setMotorRight(1)  # Adjust the speed as needed

if __name__ == "__main__":
    main()
