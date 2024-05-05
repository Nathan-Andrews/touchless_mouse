import cv2
import mediapipe as mp # type: ignore

from processpoints import *

import keyboard # type: ignore

# Initialize MediaPipe Hand model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize video capture
cap = cv2.VideoCapture(0)

left_hand = Hand(handedness=Hand.LEFT)
right_hand = Hand(handedness=Hand.RIGHT,is_mainhand=True)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the image horizontally before processing with MediaPipe
    frame_flipped = cv2.flip(frame, 1)

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)

    # Process the frame
    results = hands.process(rgb_frame)

    # reset the hands' visibility
    left_hand.visible = False
    right_hand.visible = False

    # Check if hand(s) detected
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand_label = handedness.classification[0].label

            if hand_label == 'Left':
                left_hand.update(hand_landmarks,frame_flipped.shape)

            if hand_label == 'Right':
                right_hand.update(hand_landmarks,frame_flipped.shape)
        
        right_hand.gesture()
        left_hand.gesture()

        left_hand.draw(frame_flipped)
        right_hand.draw(frame_flipped)


    # Flip the image back before displaying

    # Display the frame
    if Config.OPEN_WINDOW: cv2.imshow('Hand Tracking', frame_flipped)

    # Press 'q' or 'esc' to quit
    if cv2.waitKey(1) == ord('q') or keyboard.is_pressed('esc'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()