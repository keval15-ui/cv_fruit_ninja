import cv2
import math
import mediapipe as mp
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_drawing

class HandTracker:
    """
    Performance-Optimized Hand Tracker built for fast physical gestures.
    Includes active camera region remapping to reach screen edges easily.
    """
    def __init__(self, screen_width, screen_height, max_hands=1, smooth_factor=0.6, margin=0.08, cam_index=0):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.smooth_factor = max(0.0, min(1.0, smooth_factor))
        self.margin = margin  # 8% camera margin buffer for screen edge mapping

        self.prev_x = None
        self.prev_y = None
        self.lost_frames = 0
        self.max_lost_frames = 4

        self.mp_hands = mp_hands
        self.mp_drawing = mp_drawing
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.cap = cv2.VideoCapture(cam_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        # Avoid processing an old frame after a fast hand movement.
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def get_fingertip_position(self, show_preview=True):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None, None

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        smoothed_pos = None

        if results.multi_hand_landmarks:
            self.lost_frames = 0
            for hand_landmarks in results.multi_hand_landmarks:
                if show_preview:
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )

                tip = hand_landmarks.landmark[8]  # Index Fingertip

                # Remap camera normalized coordinates [margin, 1 - margin] to screen coordinates [0, 1]
                norm_x = (tip.x - self.margin) / (1.0 - 2 * self.margin)
                norm_y = (tip.y - self.margin) / (1.0 - 2 * self.margin)

                # Clamp within screen bounds
                norm_x = max(0.0, min(1.0, norm_x))
                norm_y = max(0.0, min(1.0, norm_y))

                raw_x = norm_x * self.screen_width
                raw_y = norm_y * self.screen_height

                # Use more smoothing while still and less smoothing during a fast
                # movement. A fixed EMA makes fast slices visibly lag behind.
                if self.prev_x is None or self.prev_y is None:
                    curr_x, curr_y = raw_x, raw_y
                else:
                    movement = math.hypot(raw_x - self.prev_x, raw_y - self.prev_y)
                    adaptive_factor = min(
                        0.95,
                        max(self.smooth_factor, 0.35 + movement / 250.0)
                    )
                    curr_x = adaptive_factor * raw_x + (1 - adaptive_factor) * self.prev_x
                    curr_y = adaptive_factor * raw_y + (1 - adaptive_factor) * self.prev_y

                # Deadzone lock for stationary hand stability
                if self.prev_x is not None and math.hypot(curr_x - self.prev_x, curr_y - self.prev_y) < 3:
                    curr_x, curr_y = self.prev_x, self.prev_y

                self.prev_x, self.prev_y = curr_x, curr_y
                smoothed_pos = (int(curr_x), int(curr_y))
                break
        else:
            self.lost_frames += 1
            if self.lost_frames <= self.max_lost_frames and self.prev_x is not None:
                smoothed_pos = (int(self.prev_x), int(self.prev_y))
            else:
                self.prev_x = None
                self.prev_y = None

        if show_preview:
            cv2.imshow("Hand Tracker Debug Preview", frame)
            cv2.waitKey(1)

        return smoothed_pos, frame

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()