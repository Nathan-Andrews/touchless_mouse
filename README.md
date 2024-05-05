# Hand Tracking

Work in progress
This project uses machine learning to track the position of your hands using the computer's camera.  It uses the landmark data returned from the ML model to detect certain hand gestures. It showcases different applications of this.

## Installation
Install dependencies:
```
python -m pip install mediapipe
python -m pip install opencv-python
python -m pip install pyautogui
```

## Usage
Run: ```python app.py```

In processpoints.py, change the flags in config to controll what is run

`DRAW_JOINTS` controls whether the joints between the landmarks are drawn in the frame

`OPEN_WINDOW` controls whether the video output should be show

`SHOW_GESTURE_NAME` turns on the gesture name mode

`CURSOR_MODE` turns on the cursor mode

`PRESENTATION_MODE` turns on the presentation mode

`GAME_MODE` turns on the game mode


## Features
This project a showcase of what can be done with this hand tracking, gesture recognition program.

The modes it includes are:

Cursor Mode: This mode controls the computer cursor with your hand movements.  Pinch the index finger on your right hand, and move your hand to move the cursor.  Pinch your right middle finger to left-click.  Pinch your right ring finger to right-click.  Pinch your left index finger, and move your left hand vertically to scroll.

Presentation Mode:  A simple mode I made to do a powerpoint presentation.  Tap your index finger and thumb together to switch to the next slide in the powerpoint.

Game Mode: Made to interact with a tetris website https://tetris.com/play-tetris.  Similar to cursor mode with an added feature.  Tap your left index finger and thumb to rotate the piece.
