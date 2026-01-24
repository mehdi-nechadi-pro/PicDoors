import cv2
import time
import numpy as np
import config
from .sensors import check_ldr_status, send_detection_signal
from .recognition import FaceEngine

class VideoManager:
    def __init__(self):
        self.ai = FaceEngine()
        
        # Gestion d'etat
        self.last_sensor_check = 0
        self.last_ai_check = 0
        self.detection_triggered = False
        self.detection_start_time = 0
        
        # Resultats visuels
        self.result = None
        self.result_end_time = 0

    def generate_stream(self):
        """Genere le flux video MJPEG frame par frame pour Flask"""
        cap = cv2.VideoCapture(config.STREAM_URL)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        while True:
            success, frame = cap.read()
            if not success:
                cap.release()
                time.sleep(0.5)
                cap = cv2.VideoCapture(config.STREAM_URL)
                continue

            frame = self._resize_and_rotate(frame)
            now = time.time()

            self._update_sensor_state(now)

            if not self.detection_triggered:
                final_image = self._get_standby_screen(frame.shape)
            else:
                self._process_active_mode(frame, now)
                final_image = frame

            ret, buffer = cv2.imencode('.jpg', final_image)
            if ret:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    def _resize_and_rotate(self, frame):
        """Applique la rotation et le redimensionnement standard"""
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        h, w = frame.shape[:2]
        new_w = 640
        new_h = int(h * (new_w / w))
        return cv2.resize(frame, (new_w, new_h))

    def _update_sensor_state(self, now):
        """Gere le reveil par capteur LDR et le timeout de veille"""
        if now - self.last_sensor_check > 0.1:
            self.last_sensor_check = now
            if check_ldr_status():
                if not self.detection_triggered:
                    print("[SYSTEM] Reveil par capteur")
                self.detection_triggered = True
                self.detection_start_time = now

        if self.detection_triggered and (now - self.detection_start_time > 5.0):
            print("[SYSTEM] Mise en veille (Timeout)")
            self.detection_triggered = False
            self.result = None

    def _process_active_mode(self, frame, now):
        """Orchestre la detection faciale et l'affichage des resultats"""
        remaining = max(0, int(5 - (now - self.detection_start_time)))
        cv2.putText(frame, f"SCAN ({remaining}s)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

        if now < self.result_end_time and self.result:
            self._draw_result(frame)
            return

        if now - self.last_ai_check >= config.CHECK_INTERVAL:
            self.last_ai_check = now
            name, score, box = self.ai.process_image(frame)
            
            if box:
                if score >= config.THRESHOLD:
                    send_detection_signal(name)
                    self.result = {"box": box, "msg": f"OK: {name}", "col": (0, 255, 0)}
                    self.result_end_time = now + 2.0
                    self.detection_triggered = False # Succes : retour en veille apres affichage
                else:
                    self.result = {"box": box, "msg": "Inconnu", "col": (0, 0, 255)}
                    self.result_end_time = now + 1.0

    def _draw_result(self, frame):
        """Dessine la bounding box et le message sur l'image"""
        if not self.result: return
        x, y, w, h = self.result['box']['x'], self.result['box']['y'], self.result['box']['w'], self.result['box']['h']
        cv2.rectangle(frame, (x, y), (x+w, y+h), self.result['col'], 2)
        cv2.putText(frame, self.result['msg'], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.result['col'], 2)

    def _get_standby_screen(self, shape):
        """Genere l'ecran noir de veille"""
        h, w = shape[:2]
        img = np.zeros((h, w, 3), np.uint8)
        cv2.putText(img, "VEILLE", (w//2 - 40, h//2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return img