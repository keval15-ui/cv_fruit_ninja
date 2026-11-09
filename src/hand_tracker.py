import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands

class HandTracker:
    """ 
    Handles camera capture, frame flipping, RGB conversion, and
    extracts screen-scaled (X, Y) pixel coordinates for the index fingertip.
    """
    def __init__(self, screen_width, screen_height, max_hands=1, min_detection_confidence=0.7):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.mp_hands = mp_hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence
        )
        self.cap = cv2.VideoCapture(0)

    def get_fingertip_position(self):
        """
        Reads frame from webcam, flips horizontally, extracts index fingertip (Landmark 8).
        Returns a tuple of ((px, py), original_frame).
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        # Mirror frame horizontally so screen movement is intuitive
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        pos = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                tip = hand_landmarks.landmark[8]  # Index Fingertip
                px = int(tip.x * self.screen_width)
                py = int(tip.y * self.screen_height)
                pos = (px, py)
                break  # Process primary hand only

        return pos, frame

    def release(self):
        """Releases webcam hardware resources."""
        if self.cap.isOpened():
            self.cap.release()