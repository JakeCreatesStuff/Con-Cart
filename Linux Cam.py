import cv2
import numpy as np
import pyvirtualcam
from pyvirtualcam import PixelFormat

CAM1 = 0
CAM2 = 1
FPS = 30

# Virtual camera resolution
CANVAS_W = 1920
CANVAS_H = 1440

# Fixed feed sizes (16:9)
TOP_W, TOP_H = 1920, 1080
BOT_W, BOT_H = 480, 270

# Layout
TOP_MARGIN = 0
GAP = 20

# Safety check (important)
required_height = TOP_MARGIN + TOP_H + GAP + BOT_H
if required_height > CANVAS_H:
    raise ValueError(
        f"Layout too tall for canvas: needs {required_height}px, "
        f"canvas is {CANVAS_H}px"
    )

cap1 = cv2.VideoCapture(CAM1)
cap2 = cv2.VideoCapture(CAM2)

with pyvirtualcam.Camera(
    width=CANVAS_W,
    height=CANVAS_H,
    fps=FPS,
    fmt=PixelFormat.BGR
) as cam:

    print(f"Using virtual cam: {cam.device}")

    while True:
        r1, f1 = cap1.read()
        r2, f2 = cap2.read()
        if not r1 or not r2:
            break

        top = cv2.resize(f1, (TOP_W, TOP_H))
        bottom = cv2.resize(f2, (BOT_W, BOT_H))

        canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)

        # Horizontal centering
        top_x = (CANVAS_W - TOP_W) // 2
        bot_x = (CANVAS_W - BOT_W) // 2

        # Vertical placement (safe)
        top_y = TOP_MARGIN
        bot_y = top_y + TOP_H + GAP

        canvas[top_y:top_y+TOP_H, top_x:top_x+TOP_W] = top
        canvas[bot_y:bot_y+BOT_H, bot_x:bot_x+BOT_W] = bottom

        cam.send(canvas)
        cam.sleep_until_next_frame()

        cv2.imshow("Preview", canvas)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap1.release()
cap2.release()
cv2.destroyAllWindows()
