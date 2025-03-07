# Gesture-Controlled Tetris Game

A modern implementation of the classic Tetris game with both keyboard and hand gesture controls using computer vision.

## Features

- Classic Tetris gameplay mechanics
- Hand gesture control using webcam
- Traditional keyboard control support
- Real-time visual feedback for gesture controls
- Score tracking and level progression
- Ghost piece preview
- Side panel with game information and controls

## Requirements

### Hardware
- Webcam
- Computer with Python support
- Sufficient lighting for hand detection

### Software Dependencies
- Python 3.x
- OpenCV
- Mediapipe
- Pygame

## Installation

1. Clone or download the project files
2. Install the required dependencies:

```bash
pip install pygame
pip install mediapipe
pip install opencv-python
pip install numpy
```

3. Ensure both Python files are in the same directory:
   - `tetris_keyboard.py`
   - `tetris_gesture_control.py`

## How to Play

### Starting the Game
Run the main game file:


### Controls

#### Keyboard Controls
- Left Arrow: Move piece left
- Right Arrow: Move piece right
- Up Arrow: Rotate piece
- Down Arrow: Soft drop
- Spacebar: Hard drop
- R: Reset game
- Q: Quit game

#### Gesture Controls
The webcam view is divided into a 3x3 grid with the following control zones:
- Left Zone: Move piece left
- Right Zone: Move piece right
- Top Zone: Rotate piece
- Bottom Zone: Soft drop
- Center Zone: Neutral (no action)

To use gesture controls:
1. Position your hand in front of the webcam
2. Use your index finger to point to the desired control zone
3. Hold position briefly to trigger the action
4. Return to neutral zone to reset

## Game Features

### Scoring System
- Line Clear: 100 points × current level
- Level increases every 10 lines cleared
- Speed increases with each level

### Visual Features
- Ghost piece shows landing position
- Next piece preview
- Score, level, and lines cleared display
- Visual feedback for gesture controls
- Grid-based gesture control interface

## Technical Details

### Files
- `tetris_keyboard.py`: Main game implementation
- `tetris_gesture_control.py`: Hand gesture control implementation

### Key Components
1. **Tetris Class**
   - Game board management
   - Piece movement and rotation
   - Collision detection
   - Scoring system

2. **HandGestureController Class**
   - Webcam input processing
   - Hand landmark detection
   - Gesture zone mapping
   - Command timing control

### Gesture Control Parameters
- Detection Confidence: 0.7
- Tracking Confidence: 0.5
- Command Cooldowns:
  - Left/Right: 0.15 seconds
  - Rotation: 0.3 seconds
  - Drop: 0.1 seconds
- Zone Threshold: 0.1 seconds

## Troubleshooting

### Common Issues

1. **Webcam Not Detected**
   - Check webcam connection
   - Verify webcam permissions
   - Try different USB port

2. **Poor Gesture Recognition**
   - Ensure good lighting
   - Keep hand within frame
   - Maintain clear background
   - Adjust position relative to camera

3. **Performance Issues**
   - Close unnecessary applications
   - Check system requirements
   - Reduce window size if needed

### Error Messages

- "Camera not found": Check webcam connection
- "Import error": Verify all dependencies are installed
- "Permission denied": Grant camera access to Python

## Development

### Project Structure
tetris/  
├── tetris_keyboard.py # Main game logic  
├── tetris_gesture_control.py # Gesture control implementation  
└── README.md # Documentation  


### Customization
- Adjust COOLDOWN_TIMES in gesture control for different response speeds
- Modify BLOCK_SIZE for different game scales
- Change colors in COLORS list for different piece colors
- Adjust BOARD_WIDTH and BOARD_HEIGHT for different game dimensions

## Contributing

Feel free to submit issues and enhancement requests!

## Acknowledgments

- Built with PyGame, OpenCV, and MediaPipe
- Inspired by classic Tetris gameplay
- Thanks to the computer vision and gaming communities
