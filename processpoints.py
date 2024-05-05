import cv2
import mediapipe as mp # type: ignore
import pyautogui # type: ignore
import math

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

screen_width, screen_height = pyautogui.size()

pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0

def move_cursor(cx,cy):
    pyautogui.moveTo(cx * screen_width * 1.3 - (screen_width * 0.15) , cy * screen_height * 1.3 - (screen_height * 0.15), duration=0)

def scroll_cursor(dy):
    pyautogui.scroll(dy * Config.SCROLL_CONSTANT)


class Config:
    MAX_PINCH_DISTANCE = 0.04
    NEUTRAL_1D_DISTANCE_THRESHOLD = 0.06
    NEUTRAL_2D_DISTANCE_THRESHOLD = 0.08
    SCROLL_CONSTANT = 50
    DRAW_JOINTS = True
    OPEN_WINDOW = True
    SHOW_GESTURE_NAMES = False
    CURSOR_MODE = True
    PRESENTATION_MODE = False
    GAME_MODE = True


class Hand:
    UP = "UP"
    DOWN = "DOWN"
    INNER = "INNER"
    OUTER = "OUTER"
    NEUTRAL = "NEUTRAL"
    NONE = "NONE"
    
    LEFT = "LEFT"
    RIGHT = "RIGHT"

    handedness = NONE # left, right
    is_mainhand = False

    thumb_state = (NONE,NONE)
    index_state = (NONE,NONE)
    middle_state = (NONE,NONE)
    ring_state = (NONE,NONE)
    pinky_state = (NONE,NONE)

    visible = False # flag for if the hand is in window

    mouse_pressed = (False,False) # of form (left_pressed,right_pressed)

    hand_landmarks = None  # contains the information for every landmark.  This is the object we get coordinates from

    current_gesture = '' # stores the current gesture of the hand to be displayed as text i.e FIST, THUMBS_UP

    last_y = -1 # the y coordinate of last frame.  Used for scrolling

    positions = {} # a dictionary that holds the x,y coordinates of each landmark.  Key is the landmark name

    def __init__(self,handedness,is_mainhand = False):
        handedness = handedness
        self.is_mainhand = is_mainhand


    def distance(self,p1,p2): # calculates the distance between 2 landmarks
        x1, y1 = self.positions[p1]
        x2, y2 = self.positions[p2]
        
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        

    def draw(self,frame): # draw to frame
        if self.visible: # draw hand skeleton
            mp_drawing.draw_landmarks(
                frame,
                self.hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
        
        if self.visible and Config.SHOW_GESTURE_NAMES: # draw name of gesture
            if Landmark.WRIST in self.positions.keys():
                x, y = self.positions[Landmark.WRIST]

                height, width, _ = frame.shape
                cx, cy = int(x * width), int(y * height)

                cv2.putText(frame, self.current_gesture, (cx - 50, cy + 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


    def update(self,hand_landmarks,dimension): # Update self using the landmark data of the current frame
        self.hand_landmarks = hand_landmarks

        self.visible = True

        positions = {}

        for idx, landmark in enumerate(hand_landmarks.landmark):
            # Get the pixel coordinates of hand landmarks
            height, width, _ = dimension
            cx, cy = landmark.x, landmark.y

            label = Landmark.getLabel(idx)
            finger = Landmark.getFingerLabel(idx)

            positions[label] = (cx, cy)
        
        self.positions = positions

        self.update_flags()
    
    def get_direction(self,p_tip,p_base): # retuns the direction flags of an individual finger in the form (LEFT/RIGHT,UP/DOWN)
        direction = (Hand.NONE,Hand.NONE)

        if p_tip in self.positions.keys() and p_base in self.positions.keys():
            xt, yt = self.positions[p_tip]
            xk, yk = self.positions[p_base]

            if xt - xk > Config.NEUTRAL_1D_DISTANCE_THRESHOLD: # Inner and outer is flipped on the left hand
                directionX = Hand.OUTER if self.handedness == Hand.RIGHT else Hand.INNER
            elif xk - xt > Config.NEUTRAL_1D_DISTANCE_THRESHOLD:
                directionX = Hand.INNER if self.handedness == Hand.RIGHT else Hand.OUTER
            else:
                directionX = Hand.NEUTRAL
            if yt - yk > Config.NEUTRAL_1D_DISTANCE_THRESHOLD:
                directionY = Hand.DOWN
            elif yk - yt > Config.NEUTRAL_1D_DISTANCE_THRESHOLD:
                directionY = Hand.UP
            else:
                directionY = Hand.NEUTRAL
            
            direction = (directionX,directionY)
        
        return direction
    
    def update_flags(self): # updates the direction flags of each finger.
        if self.visible:
            if Landmark.THUMB_TIP in self.positions.keys() and Landmark.THUMB_MCP in self.positions.keys():
                self.thumb_state = self.get_direction(Landmark.THUMB_TIP,Landmark.THUMB_MCP)
            if Landmark.INDEX_FINGER_TIP in self.positions.keys() and Landmark.INDEX_FINGER_MCP in self.positions.keys():
                self.index_state = self.get_direction(Landmark.INDEX_FINGER_TIP,Landmark.INDEX_FINGER_MCP)
            if Landmark.MIDDLE_FINGER_TIP in self.positions.keys() and Landmark.MIDDLE_FINGER_MCP in self.positions.keys():
                self.middle_state = self.get_direction(Landmark.MIDDLE_FINGER_TIP,Landmark.MIDDLE_FINGER_MCP)
            if Landmark.RING_FINGER_TIP in self.positions.keys() and Landmark.RING_FINGER_MCP in self.positions.keys():
                self.ring_state = self.get_direction(Landmark.RING_FINGER_TIP,Landmark.RING_FINGER_MCP)
            if Landmark.PINKY_TIP in self.positions.keys() and Landmark.PINKY_MCP in self.positions.keys():
                self.pinky_state = self.get_direction(Landmark.PINKY_TIP,Landmark.PINKY_MCP)
            
        # self.print_flags()
                
    def print_flags(self):
        if self.visible:
            print(f"thumb :{self.thumb_state}")
            print(f"index :{self.index_state}")
            print(f"middle :{self.middle_state}")
            print(f"ring :{self.ring_state}")
            print(f"pinky :{self.pinky_state}")
            print("+-------------------+")


    def mouse(self): # move cursor
        if self.visible and Landmark.INDEX_FINGER_TIP in self.positions.keys():
            cx,cy = self.positions[Landmark.INDEX_FINGER_TIP]
            move_cursor(cx,cy)


    def scroll(self): # scroll
        if self.visible and Landmark.INDEX_FINGER_TIP in self.positions.keys():
            cy = self.positions[Landmark.INDEX_FINGER_TIP][1]

            if not self.last_y < 0:
                dy = self.last_y - cy
                scroll_cursor(dy)
            
            self.last_y = cy

    
    def gesture(self): # detect gesture and perform related actions
        if self.visible and (Config.CURSOR_MODE or Config.GAME_MODE) and self.is_mainhand: # mainhand actions (usually right hand)
            if (self.distance(Landmark.THUMB_TIP,Landmark.INDEX_FINGER_TIP) < Config.MAX_PINCH_DISTANCE): # if index and thumb pinched then move mouse
                self.mouse()
            

            if (self.distance(Landmark.THUMB_TIP,Landmark.MIDDLE_FINGER_TIP) < Config.MAX_PINCH_DISTANCE): # if middle and thumb pinched left click
                if not self.mouse_pressed[0]:
                    pyautogui.mouseDown()
                    self.mouse_pressed = (True,self.mouse_pressed[1])
            
            elif self.mouse_pressed[0]: # release left click
                pyautogui.mouseUp()
                self.mouse_pressed = (False,self.mouse_pressed[1])
            
            if (self.distance(Landmark.THUMB_TIP,Landmark.RING_FINGER_TIP) < Config.MAX_PINCH_DISTANCE and not Config.GAME_MODE): # if ring finger right click
                if not self.mouse_pressed[1]:
                    pyautogui.mouseDown(button="right")
                    self.mouse_pressed = (self.mouse_pressed[0],True)

            elif self.mouse_pressed[1] and not Config.GAME_MODE: # release right click
                pyautogui.mouseUp(button="right")
                self.mouse_pressed = (self.mouse_pressed[0],False)

        if self.visible and Config.CURSOR_MODE and not self.is_mainhand: # offhand actions (usually left hand
            if (self.distance(Landmark.THUMB_TIP,Landmark.INDEX_FINGER_TIP) < Config.MAX_PINCH_DISTANCE): # if index and thumb pinched then move mouse
                self.scroll()
            else:
                self.last_y = -1
        
        if self.visible and Config.SHOW_GESTURE_NAMES:
            self.current_gesture = Gesture.NEUTRAL

            if (self.index_state == (Hand.NEUTRAL,Hand.NEUTRAL) and # thumbs up
                self.middle_state == (Hand.NEUTRAL,Hand.NEUTRAL) and
                self.ring_state == (Hand.NEUTRAL,Hand.NEUTRAL) and
                self.pinky_state == (Hand.NEUTRAL,Hand.NEUTRAL) and
                self.thumb_state == (Hand.NEUTRAL,Hand.UP) and
                self.distance(Landmark.THUMB_TIP,Landmark.INDEX_FINGER_PIP) > 0.1):
                self.current_gesture = Gesture.THUMBS_UP
            elif (self.index_state == (Hand.NEUTRAL,Hand.NEUTRAL) and # thumbs up
                self.middle_state == (Hand.NEUTRAL,Hand.NEUTRAL) and
                self.ring_state == (Hand.NEUTRAL,Hand.NEUTRAL) and
                self.pinky_state == (Hand.NEUTRAL,Hand.NEUTRAL) and
                self.thumb_state == (Hand.NEUTRAL,Hand.DOWN) and
                self.distance(Landmark.THUMB_TIP,Landmark.INDEX_FINGER_PIP) > 0.1):
                self.current_gesture = Gesture.THUMBS_DOWN
            elif (self.index_state == (Hand.NEUTRAL,Hand.NEUTRAL) and # thumbs up
                self.middle_state == (Hand.NEUTRAL,Hand.NEUTRAL) and
                self.ring_state == (Hand.NEUTRAL,Hand.NEUTRAL) and
                self.pinky_state == (Hand.NEUTRAL,Hand.NEUTRAL) and
                self.distance(Landmark.THUMB_TIP,Landmark.INDEX_FINGER_PIP) < 0.1):
                self.current_gesture = Gesture.FIST
            
        if not self.visible:
            self.last_y = -1
        
        if self.visible and Config.PRESENTATION_MODE and self.is_mainhand: # presentation mode
            if (self.distance(Landmark.THUMB_TIP,Landmark.INDEX_FINGER_TIP) < Config.MAX_PINCH_DISTANCE):
                if not self.mouse_pressed[0]:
                    pyautogui.press('space')
                    self.mouse_pressed = (True,self.mouse_pressed[1])
            
            elif self.mouse_pressed[0]:
                self.mouse_pressed = (False,self.mouse_pressed[1])
        

        if self.visible and Config.GAME_MODE and not self.is_mainhand: # game mode
            if (self.distance(Landmark.THUMB_TIP,Landmark.INDEX_FINGER_TIP) < Config.MAX_PINCH_DISTANCE):
                if not self.mouse_pressed[1]:
                    pyautogui.press('z')
                    self.mouse_pressed = (self.mouse_pressed[0],True)
            
            elif self.mouse_pressed[1]:
                self.mouse_pressed = (self.mouse_pressed[0],False)





    
class Gesture:
    THUMBS_UP = "Thumbs Up"
    THUMBS_DOWN = "Thumbs Down"
    FIST = "Fist"
    NEUTRAL = "Neutral"



class Landmark:
    WRIST = "WRIST"
    THUMB_CMC = "THUMB_CMC"
    THUMB_MCP = "THUMB_MCP"
    THUMB_IP = "THUMB_IP"
    THUMB_TIP = "THUMB_TIP"
    INDEX_FINGER_MCP = "INDEX_FINGER_MCP"
    INDEX_FINGER_PIP = "INDEX_FINGER_PIP"
    INDEX_FINGER_DIP = "INDEX_FINGER_DIP"
    INDEX_FINGER_TIP = "INDEX_FINGER_TIP"
    MIDDLE_FINGER_MCP = "MIDDLE_FINGER_MCP"
    MIDDLE_FINGER_PIP = "MIDDLE_FINGER_PIP"
    MIDDLE_FINGER_DIP = "MIDDLE_FINGER_DIP"
    MIDDLE_FINGER_TIP = "MIDDLE_FINGER_TIP"
    RING_FINGER_MCP = "RING_FINGER_MCP"
    RING_FINGER_PIP = "RING_FINGER_PIP"
    RING_FINGER_DIP = "RING_FINGER_DIP"
    RING_FINGER_TIP = "RING_FINGER_TIP"
    PINKY_MCP = "PINKY_MCP"
    PINKY_PIP = "PINKY_PIP"
    PINKY_DIP = "PINKY_DIP"
    PINKY_TIP = "PINKY_TIP"

    THUMB = "THUMB"
    INDEX = "INDEX"
    MIDDLE = "MIDDLE"
    RING = "RING"
    PINKY = "PINKY"

    @staticmethod
    def getLabel(idx):
        return mp_hands.HandLandmark(idx).name
    
    @staticmethod
    def getFingerLabel(idx):
        label = Landmark.getLabel(idx)

        return label.split("_")[0]