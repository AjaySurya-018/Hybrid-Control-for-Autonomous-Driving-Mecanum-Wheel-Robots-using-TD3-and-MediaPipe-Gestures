import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

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

cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()

    if not success:
      print("Ignoring empty camera frame.")
      continue
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
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
