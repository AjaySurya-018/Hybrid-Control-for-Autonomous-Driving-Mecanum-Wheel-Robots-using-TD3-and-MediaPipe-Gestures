import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model
import RPi.GPIO as io
import time

# Initialize GPIO pins for motor control
io.setmode(io.BCM)
io.setwarnings(False)

# Define GPIO pins for motor control
leftMotor_DIR_pin = 22
rightMotor_DIR_pin = 23
leftMotor_PWM_pin = 17
rightMotor_PWM_pin = 18

io.setup(leftMotor_DIR_pin, io.OUT)
io.setup(rightMotor_DIR_pin, io.OUT)
io.setup(leftMotor_PWM_pin, io.OUT)
io.setup(rightMotor_PWM_pin, io.OUT)

leftMotorPWM = io.PWM(leftMotor_PWM_pin, 1000)
rightMotorPWM = io.PWM(rightMotor_PWM_pin, 1000)

leftMotorPWM.start(0)
rightMotorPWM.start(0)

# Constant values
PWM_MAX = 100

# Function to set motor speeds for the left motor
def setLeftMotorSpeed(speed):
    # Ensure speed limit is respected
    if speed > 1:
        speed = 1
    elif speed < -1:
        speed = -1
    
    # Set motor direction
    if speed >= 0:
        io.output(leftMotor_DIR_pin, False)
    else:
        io.output(leftMotor_DIR_pin, True)
    
    # Set motor power
    pwm = int(PWM_MAX * abs(speed))
    leftMotorPWM.ChangeDutyCycle(pwm)

# Function to set motor speeds for the right motor
def setRightMotorSpeed(speed):
    # Ensure speed limit is respected
    if speed > 1:
        speed = 1
    elif speed < -1:
        speed = -1
    
    # Set motor direction
    if speed >= 0:
        io.output(rightMotor_DIR_pin, False)
    else:
        io.output(rightMotor_DIR_pin, True)
    
    # Set motor power
    pwm = int(PWM_MAX * abs(speed))
    rightMotorPWM.ChangeDutyCycle(pwm)

# Mapping gestures to robot actions
def map_gesture_to_action(gesture):
    if gesture == "stop":
        # Move forward slowly to simulate a stop
        setLeftMotorSpeed(0.2)
        setRightMotorSpeed(0.2)
    elif gesture == "fist":
        setLeftMotorSpeed(-0.5)
        setRightMotorSpeed(-0.5)
        time.sleep(1)  # Assuming a delay of 1 second to move backward
        setLeftMotorSpeed(0)
        setRightMotorSpeed(0)
    elif gesture == "thumbs up":
        setLeftMotorSpeed(0.5)
        setRightMotorSpeed(-0.5)
    elif gesture == "thumbs down":
        setLeftMotorSpeed(-0.5)
        setRightMotorSpeed(0.5)
    elif gesture == "call me":
        setLeftMotorSpeed(1)
        setRightMotorSpeed(1)
    elif gesture == "peace":
        setLeftMotorSpeed(0.2)
        setRightMotorSpeed(0.2)

# initialize mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Load the gesture recognizer model
model = load_model('mp_hand_gesture')

# Load class names
f = open('gesture.names', 'r')
classNames = f.read().split('\n')
f.close()

# Initialize the webcam
cap = cv2.VideoCapture(0)

while True:
    # Read each frame from the webcam
    _, frame = cap.read()

    x, y, c = frame.shape

    # Flip the frame vertically
    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Get hand landmark prediction
    result = hands.process(framergb)
    
    recognized_gesture = ''

    # post process the result
    if result.multi_hand_landmarks:
        landmarks = []
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                lmx = int(lm.x * x)
                lmy = int(lm.y * y)
                landmarks.append([lmx, lmy])

            # Predict gesture
            prediction = model.predict([landmarks])
            classID = np.argmax(prediction)
            recognized_gesture = classNames[classID]
    
    # Perform the corresponding action based on the recognized gesture
    map_gesture_to_action(recognized_gesture)

    if cv2.waitKey(1) == ord('q'):
        break

# release the webcam and clean up GPIO
cap.release()
cv2.destroyAllWindows()
leftMotorPWM.stop()
rightMotorPWM.stop()
io.cleanup()
