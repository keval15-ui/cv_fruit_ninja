import cv2
import math
import threading
import time
import mediapipe as mp
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_drawing

class HandTracker:
    """
    Threaded, High-Speed Hand Tracker built to eliminate input lag.
    Processes camera frames in a background thread to prevent Pygame thread blocking.
    """
    def __init__(self, screen_width, screen_height, max_hands=1, margin=0.08, cam_index=0):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.margin = margin

        # Spatial Position & Lock State
        self.latest_pos = None
        self.latest_frame = None
        self.prev_x = None
        self.prev_y = None
        self.lost_frames = 0
        self.max_lost_frames = 5

        # MediaPipe Solutions
        self.mp_hands = mp_hands
        self.mp_drawing = mp_drawing
        
        # Use the more accurate model for steadier landmark detection.
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            model_complexity=1,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4
        )
        
        # Camera Setup with Buffer Size 1 to eliminate frame queue delay
        self.cap = cv2.VideoCapture(cam_index)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"Unable to open camera {cam_index}. "
                "Check camera permissions or choose another camera index."
            )

        # Thread Control
        self.running = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._capture_and_process_loop, daemon=True)
        self.thread.start()

    def _is_pointing_gesture(self, hand_landmarks):
        """Validates index finger extension away from wrist."""
        lm = hand_landmarks.landmark
        wrist = lm[0]

        dist_index_tip = math.hypot(lm[8].x - wrist.x, lm[8].y - wrist.y)
        dist_index_pip = math.hypot(lm[6].x - wrist.x, lm[6].y - wrist.y)
        if dist_index_tip <= dist_index_pip * 1.15:
            return False

        middle_folded = math.hypot(lm[12].x - wrist.x, lm[12].y - wrist.y) < math.hypot(lm[10].x - wrist.x, lm[10].y - wrist.y) * 1.1
        ring_folded   = math.hypot(lm[16].x - wrist.x, lm[16].y - wrist.y) < math.hypot(lm[14].x - wrist.x, lm[14].y - wrist.y) * 1.1
        pinky_folded  = math.hypot(lm[20].x - wrist.x, lm[20].y - wrist.y) < math.hypot(lm[18].x - wrist.x, lm[18].y - wrist.y) * 1.1

        return sum([middle_folded, ring_folded, pinky_folded]) >= 2

    def _capture_and_process_loop(self):
        """Background thread continuously fetching frames and running ML inference."""
        while self.running:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                time.sleep(0.005)
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False
            results = self.hands.process(rgb_frame)
            rgb_frame.flags.writeable = True

            smoothed_pos = None

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS
                    )

                    self.lost_frames = 0
                    tip = hand_landmarks.landmark[8]
                    tip_pixel = (
                        int(tip.x * frame.shape[1]),
                        int(tip.y * frame.shape[0])
                    )
                    cv2.circle(frame, tip_pixel, 8, (0, 255, 255), -1)

                    # Remap camera margin buffer to screen resolution
                    norm_x = (tip.x - self.margin) / (1.0 - 2 * self.margin)
                    norm_y = (tip.y - self.margin) / (1.0 - 2 * self.margin)

                    norm_x = max(0.0, min(1.0, norm_x))
                    norm_y = max(0.0, min(1.0, norm_y))

                    raw_x = norm_x * self.screen_width
                    raw_y = norm_y * self.screen_height

                    if self.prev_x is None or self.prev_y is None:
                        curr_x, curr_y = raw_x, raw_y
                    else:
                        movement = math.hypot(raw_x - self.prev_x, raw_y - self.prev_y)
                        if movement < 5:
                            curr_x, curr_y = self.prev_x, self.prev_y
                        else:
                            dynamic_smooth = 0.95 if movement > 35 else 0.78
                            curr_x = dynamic_smooth * raw_x + (1 - dynamic_smooth) * self.prev_x
                            curr_y = dynamic_smooth * raw_y + (1 - dynamic_smooth) * self.prev_y

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

            with self.lock:
                self.latest_pos = smoothed_pos
                self.latest_frame = frame

    def get_fingertip_position(self, show_preview=True, is_calibrated=False):
        """Fetches the latest calculated fingertip coordinate non-blockingly."""
        with self.lock:
            pos = self.latest_pos
            frame = self.latest_frame

        if show_preview and frame is not None:
            cv2.imshow("Hand Tracker Debug Preview", frame)
            cv2.waitKey(1)

        return pos, frame

    def release(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()