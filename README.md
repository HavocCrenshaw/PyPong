# PyPong
A implementation of the classic Pong in Python! Inspired by a teaching project
I did where I had taught somebody how to code a Pong game with Python. I decided
to go more "all out" with my own version.

![PyPong in Action](./pypong-in-action.png)

# Requirements & Running
To run, you should have Python and PyGame installed. Python 3.13.5 and Pygame
2.6.1 are the canonical versions.

https://python.org/<br>
https://pygame.org/

Then, just simply:<br>
`$ python3 pypong.py`

# Configuration
The game can be fairly easily configured by changing the constant values at the
top. Pretty much every reasonable change can be made there, however, it should
be no issue to go into the code and change specifics.

For general reference, the settings you may want to change the most are:<br>
- `SCREEN_WIDTH`, `SCREEN_HEIGHT`: Dimensions of the window.<br>
- `ELEMENT_WIDTH`: The base scale from which all "elements" derive.<br>
- `NUM_CENTER_DOTS`, `CENTER_DOT_PADDING`: The number of dots in the center, and
the padding between dots.<br>
- `MOV_INC`: How fast the paddles go.<br>
- `BALL_SPEED`: How fast the ball goes.<br>
- `COLOR_WHITE`: Technically a very light grey by default, can be changed to any
color desired.

# TODO
Add an AI opponent!<br>
UX flair & polish.
