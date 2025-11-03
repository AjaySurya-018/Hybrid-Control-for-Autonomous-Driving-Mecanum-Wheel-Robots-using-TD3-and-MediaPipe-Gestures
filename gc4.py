import cv2
import mediapipe as mp
import numpy as np
import RPi.GPIO as io
from picamera.array import PiRGBArray
from picamera import PiCamera

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Set GPIO mode and pins
io.setmode(io.BCM)

# Constant values
PWM_MAX = 100

# Disable warning from GPIO
io.setwarnings(False)

# Define GPIO pins for motor control
leftMotor_DIR_pin = 22
io.setup(leftMotor_DIR_pin, io.OUT)

rightMotor_DIR_pin = 23
io.setup(rightMotor_DIR_pin, io.OUT)

io.output(leftMotor_DIR_pin, False)
io.output(rightMotor_DIR_pin, False)

leftMotor_PWM_pin = 17
rightMotor_PWM_pin = 18

io.setup(leftMotor_PWM_pin, io.OUT)
io.setup(rightMotor_PWM_pin, io.OUT)

# MAX Frequency 20 Hz
leftMotorPWM = io.PWM(leftMotor_PWM_pin, 1000)
rightMotorPWM = io.PWM(rightMotor_PWM_pin, 1000)

leftMotorPWM.start(0)
leftMotorPWM.ChangeDutyCycle(0)

rightMotorPWM.start(0)
rightMotorPWM.ChangeDutyCycle(0)

leftMotorPower = 0
rightMotorPower = 0

def setMotorLeft(power):
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
    leftMotorPWM.ChangeDutyCycle(pwm)

def setMotorRight(power):
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
    rightMotorPWM.ChangeDutyCycle(pwm)

# Define your gesture dictionary here
gesture_dict = {
    0: 'Closed Fist',
    1: '1 Finger',
    2: '2 Fingers',
    3: '3 Fingers',
    4: '4 Fingers',
    5: 'Open Hand',
}

def recognize_gesture(hand_landmarks):
    # Count the number of fingers raised
    # We consider a finger as raised if the distance between the tips of the fingers is above a certain threshold
    finger_tips = [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]
    count_fingers = 0
    for i in range(1, 5):
        for j in range(i):
            distance = np.sqrt((hand_landmarks.landmark[finger_tips[i]].x - hand_landmarks.landmark[finger_tips[j]].x)**2 + (hand_landmarks.landmark[finger_tips[i]].y - hand_landmarks.landmark[finger_tips[j]].y)**2)
            if distance > 0.1:
                count_fingers += 1
                break

    # Return the label of the recognized gesture
    return gesture_dict[count_fingers]

# Initialize the camera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# Allow the camera to warm up
time.sleep(0.1)

with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        # Recognize gesture and assign label
        gesture_label = recognize_gesture(hand_landmarks)
        # Display the label on the video preview
        cv2.putText(image, gesture_label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Control the robot's motors based on the recognized gesture
        if gesture_label == '1 Finger':
            setMotorLeft(0.02)
            setMotorRight(0.02)
        elif gesture_label == '2 Fingers':
            setMotorLeft(-0.02)
            setMotorRight(-0.02)
        elif gesture_label == '3 Fingers':
            setMotorLeft(0.02)
            setMotorRight(-0.02)
        elif gesture_label == '4 Fingers':
            setMotorLeft(-0.02)
            setMotorRight(0.02)
        elif gesture_label == 'Closed Fist':
            setMotorLeft(0.04)
            setMotorRight(0.04)

    cv2.imshow('MediaPipe Hands', image)
    key = cv2.waitKey(1) & 0xFF

    # Clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # If the `q` key was pressed, break from the loop
    if key == ord("q"):
      break

cv2.destroyAllWindows()
