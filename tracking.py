import cv2
import mediapipe as mp
import pyautogui
from sys import exit

#hand detection code edited from MediaPipe hand tracking api

'''#project overview
#track hand position
#recognize gestures
#gestures trigger mouse + shortcuts
#speech to text for typing (only when doing a certain hand signal)'''

settings = {
    "show_tracking_camera": False,
    "track_to_mouse": True,
    "time_out": False,
    "movement_thresh_hold": .001,
    "drag_movement_duration": 0
}

screen_width, screen_height = pyautogui.size()

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

tick = 0
action_cooldown = 0
x_old = []
y_old = []
mouse_down = False
mouse_down_timer = 0
kill_flag = False


action_age = {
    "swipe_left": 0,
    "swipe_right": 0
}

pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = settings["drag_movement_duration"]

with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    print("Camera starting...")
    while cap.isOpened() and not kill_flag:
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        results = hands.process(image)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                hand_count = 0
                for hand_object in results.multi_handedness:

                    hand = hand_object.classification[0].label
                    #print(hand)
                    if hand == "Left":
                        #print("Right hand", hand_object)
                        hand_count += 1

                    if hand == "Right":
                        #print("Left hand", hand_object)
                        hand_count += 1

                if hand_count == 1:
                    index0_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].x
                    index0_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y
                    index1_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].x
                    index1_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y
                    index2_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].x
                    index2_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].y
                    index3_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
                    index3_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y

                    middle0_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x
                    middle0_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y
                    middle1_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].x
                    middle1_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
                    middle2_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP].x
                    middle2_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP].y
                    middle3_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x
                    middle3_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y

                    ring0_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].x
                    ring0_y = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y
                    ring1_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].x
                    ring1_y = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y
                    ring2_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP].x
                    ring2_y = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP].y
                    ring3_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x
                    ring3_y = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y

                    pinky0_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].x
                    pinky0_y = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].y
                    pinky1_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].x
                    pinky1_y = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y
                    pinky2_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP].x
                    pinky2_y = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP].y
                    pinky3_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].x
                    pinky3_y = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y

                    thumb0_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC].x
                    thumb0_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC].y
                    thumb1_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP].x
                    thumb1_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP].y
                    thumb2_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x
                    thumb2_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].y
                    thumb3_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
                    thumb3_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y

                    wrist_x = 1 - hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
                    wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y

                    x = (index0_x + middle0_x + ring0_x + pinky0_x + wrist_x * 4) / 8 #- 0.1
                    y = (index0_y + middle0_y + ring0_y + pinky0_y + wrist_y * 4) / 8 #- 0.1

                    image = cv2.circle(image, (int((1- x) * 1280), int(y * 720)), 10, (237, 219, 104), thickness=-1)
                    #image = cv2.circle(image, (1280, 720), 7, (104, 219, 237), thickness=-1)


                    x_old.append(x)
                    if len(x_old) > 3: x_old.pop(0)
                    y_old.append(y)
                    if len(y_old) > 3: y_old.pop(0)

                    velocity_x = (x_old[-1] - x_old[0])
                    velocity_y = (y_old[-1] - y_old[0])


                try:
                    if index1_y < index2_y < index3_y:
                        index_down = True
                    else:
                        index_down = False

                    if middle1_y < middle2_y < middle3_y:
                        middle_down = True
                    else:
                        middle_down = False

                    if ring1_y < ring2_y < ring3_y:
                        ring_down = True
                    else:
                        ring_down = False

                    if pinky1_y < pinky2_y < pinky3_y:
                        pinky_down = True
                    else:
                        pinky_down = False

                    if ring_down and pinky_down and middle_down and index_down and action_cooldown == 0 and settings["track_to_mouse"]:
                        if not mouse_down:
                            #if all fingers down, clicks the mouse
                            print("trigger click")
                            #pyautogui.click()
                            pyautogui.mouseDown()
                            mouse_down = True
                            #action_cooldown = 7
                        mouse_down_timer += 1
                    elif mouse_down:
                        print("end click")
                        pyautogui.mouseUp()
                        action_cooldown = 7
                        mouse_down = False
                        mouse_down_timer = 0
                    """if index_down and middle_down and ring_down and not pinky_down and action_cooldown == 0:
                        print("trigger right click")
                        pyautogui.rightClick()
                        action_cooldown = 7"""
                    if ring_down and pinky_down and not middle_down and not index_down and velocity_x > 0.1 and action_cooldown == 0:
                        action_age["swipe_left"] += 1
                        if action_age["swipe_left"] == 2:
                            print("trigger swipe left")
                            pyautogui.keyDown('ctrl')
                            pyautogui.keyDown('left')
                            pyautogui.keyUp('left')
                            pyautogui.keyUp('ctrl')
                            action_cooldown = 12
                            action_age["swipe_left"] = 0
                    elif action_age["swipe_left"] > 0: action_age["swipe_left"] = 0
                    if ring_down and pinky_down and not middle_down and not index_down and velocity_x < -0.1 and action_cooldown == 0:
                        action_age["swipe_right"] += 1
                        if action_age["swipe_right"] == 2:
                            print("trigger swipe right")
                            pyautogui.keyDown('ctrl')
                            pyautogui.keyDown('right')
                            pyautogui.keyUp('right')
                            pyautogui.keyUp('ctrl')
                            action_cooldown = 12
                            action_age["swipe_right"] = 0
                    elif action_age["swipe_right"] > 0: action_age["swipe_right"] = 0
                    if ring_down and pinky_down and index_down and not middle_down:
                        print("Killed process")
                        kill_flag = True

                    if abs(x_old[-1] - x_old[0]) > settings["movement_thresh_hold"] and abs(
                            y_old[-1] - y_old[0]) > settings["movement_thresh_hold"] and settings["track_to_mouse"]:

                        pyautogui.moveTo(x * screen_width * 1.1, y * screen_height * 1.1, duration=settings["drag_movement_duration"])

                except:
                    print("not all values found")

                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
        else:
            if mouse_down:
                pyautogui.mouseUp()
                mouse_down = False


        if settings["show_tracking_camera"]: cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
        tick += 1
        if action_cooldown > 0:
            action_cooldown -= 1
        if tick >= 1000 and settings["time_out"]:
            print("time limit reached")
            break

cap.release()
