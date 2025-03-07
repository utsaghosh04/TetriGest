import cv2
import mediapipe as mp
import numpy as np
import pygame
import time

class HandGestureController:
    def __init__(self):
        # Initialize MediaPipe hand tracking
        self.mediapipe_hands = mp.solutions.hands
        self.hand_detector = self.mediapipe_hands.Hands(
            static_image_mode=False,      # For video processing
            max_num_hands=1,              # Track only one hand
            min_detection_confidence=0.7,  # Higher value = more accurate but slower
            min_tracking_confidence=0.5    # Balance between accuracy and speed
        )
        self.hand_drawer = mp.solutions.drawing_utils
        
        # Initialize webcam capture
        self.webcam = cv2.VideoCapture(0)
        
        # Define webcam window dimensions
        self.WINDOW_WIDTH = 640
        self.WINDOW_HEIGHT = 480
        
        # Create a 3x3 grid for controls
        self.GRID_COLUMNS = 3
        self.GRID_ROWS = 3
        self.zone_width = self.WINDOW_WIDTH // self.GRID_COLUMNS
        self.zone_height = self.WINDOW_HEIGHT // self.GRID_ROWS
        
        # Map control zones to grid positions
        self.CONTROL_ZONES = {
            'LEFT': (0, 1),    # Left column, middle row
            'RIGHT': (2, 1),   # Right column, middle row
            'ROTATE': (1, 0),  # Middle column, top row
            'DOWN': (1, 2),    # Middle column, bottom row
            'NEUTRAL': (1, 1)  # Middle column, middle row (safe zone)
        }
        
        # Time tracking for each command to prevent rapid-fire
        self.last_action_time = {
            'LEFT': 0,
            'RIGHT': 0,
            'ROTATE': 0,
            'DOWN': 0
        }
        
        # Delay between actions (in seconds) for smooth control
        self.ACTION_DELAYS = {
            'LEFT': 0.15,      # Quick side movement
            'RIGHT': 0.15,     # Quick side movement
            'ROTATE': 0.3,     # Slower rotation to prevent spin
            'DOWN': 0.1        # Fast dropping
        }
        
        # Timing for zone activation
        self.zone_entry_timestamp = 0
        self.ACTIVATION_DELAY = 0.1  # Time needed in zone to trigger action
        
        # Track finger position
        self.previous_zone = None
        self.zone_entry_time = None
        
    def get_current_zone(self, finger_x, finger_y):
        """Convert finger coordinates to grid zone position"""
        grid_x = finger_x // self.zone_width
        grid_y = finger_y // self.zone_height
        return (grid_x, grid_y)
        
    def can_perform_action(self, action_type):
        """Check if enough time has passed to perform action again"""
        current_time = time.time()
        if current_time - self.last_action_time[action_type] >= self.ACTION_DELAYS[action_type]:
            self.last_action_time[action_type] = current_time
            return True
        return False
        
    def get_finger_position(self):
        """Main method to process webcam input and return control commands"""
        # Capture webcam frame
        success, camera_image = self.webcam.read()
        if not success:
            return None
        
        # Mirror image for intuitive controls
        camera_image = cv2.flip(camera_image, 1)
        rgb_image = cv2.cvtColor(camera_image, cv2.COLOR_BGR2RGB)
        hand_tracking_results = self.hand_detector.process(rgb_image)
        
        # Draw control grid
        self._draw_control_grid(camera_image)
        
        # Draw zone labels
        self._draw_zone_labels(camera_image)
        
        current_action = None
        current_time = time.time()
        
        # Process hand landmarks if detected
        if hand_tracking_results.multi_hand_landmarks:
            for hand_landmarks in hand_tracking_results.multi_hand_landmarks:
                # Visualize hand landmarks
                self.hand_drawer.draw_landmarks(
                    camera_image, 
                    hand_landmarks, 
                    self.mediapipe_hands.HAND_CONNECTIONS
                )
                
                # Get index fingertip position
                fingertip = hand_landmarks.landmark[8]  # Index fingertip landmark
                finger_x = int(fingertip.x * self.WINDOW_WIDTH)
                finger_y = int(fingertip.y * self.WINDOW_HEIGHT)
                
                # Show fingertip position
                self._draw_fingertip_marker(camera_image, finger_x, finger_y)
                
                # Get current control zone
                current_zone = self.get_current_zone(finger_x, finger_y)
                
                # Handle zone transitions
                if current_zone != self.previous_zone:
                    self.zone_entry_time = current_time
                    self.previous_zone = current_zone
                
                # Check for valid control actions
                if self.zone_entry_time is not None:
                    time_in_zone = current_time - self.zone_entry_time
                    
                    # Check all control zones
                    for action, zone in self.CONTROL_ZONES.items():
                        if current_zone == zone and action != 'NEUTRAL':
                            if (time_in_zone >= self.ACTIVATION_DELAY and 
                                self.can_perform_action(action)):
                                current_action = action
                                # Visual feedback for action
                                cv2.circle(camera_image, (finger_x, finger_y), 
                                         15, (0, 0, 255), 2)
        
        # Show current action on screen
        if current_action:
            cv2.putText(camera_image, f"Action: {current_action}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display webcam feed
        cv2.imshow('Hand Gesture Controls', camera_image)
        cv2.waitKey(1)
        
        return current_action
    
    def _draw_control_grid(self, image):
        """Draw the 3x3 control grid"""
        # Vertical lines
        for i in range(1, self.GRID_COLUMNS):
            cv2.line(image, 
                    (i * self.zone_width, 0), 
                    (i * self.zone_width, self.WINDOW_HEIGHT), 
                    (255, 255, 255), 2)
        # Horizontal lines
        for i in range(1, self.GRID_ROWS):
            cv2.line(image, 
                    (0, i * self.zone_height), 
                    (self.WINDOW_WIDTH, i * self.zone_height), 
                    (255, 255, 255), 2)
    
    def _draw_zone_labels(self, image):
        """Draw labels for each control zone"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        for action, (col, row) in self.CONTROL_ZONES.items():
            x = col * self.zone_width + self.zone_width // 2 - 30
            y = row * self.zone_height + self.zone_height // 2
            cv2.putText(image, action, (x, y), font, 1, (255, 255, 0), 2)
    
    def _draw_fingertip_marker(self, image, x, y):
        """Draw marker at fingertip position"""
        cv2.circle(image, (x, y), 10, (0, 255, 0), -1)
    
    def cleanup(self):
        """Release webcam and close windows"""
        self.webcam.release()
        cv2.destroyAllWindows()

# Test the gesture controller independently
def main():
    controller = HandGestureController()
    
    try:
        while True:
            action = controller.get_finger_position()
            if action:
                print(f"Detected gesture: {action}")
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        controller.cleanup()

if __name__ == "__main__":
    main() 