from fastapi import FastAPI, UploadFile, File, Response
from inference_sdk import InferenceHTTPClient
import cv2
import numpy as np
import os
import uuid

app = FastAPI()


ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "zG3akc4R6w2IEhak3GyS")

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)
MODEL_ID = "dark-circle-wj25f/1"

@app.get("/")
async def root():
    return {"message": "Dark Circle Detection API is Running!", "docs": "/docs"}

@app.post("/analyze_and_show")
async def analyze_and_show(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    temp_filename = f"temp_{uuid.uuid4()}.jpg"
    cv2.imwrite(temp_filename, image)

    try:
        result = CLIENT.infer(temp_filename, model_id=MODEL_ID)
        predictions = result['predictions']

        overlay = image.copy()
        for pred in predictions:
            x, y, w, h = int(pred['x']), int(pred['y']), int(pred['width']), int(pred['height'])
            x1, y1, x2, y2 = int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + h / 2)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (40, 40, 40), -1)

        image_combined = cv2.addWeighted(overlay, 0.4, image, 0.6, 0)

        height, width = image.shape[:2]
        base_width = 800.0
        font_scale = max(0.5, min(2.5, width / base_width))
        thickness = max(1, int(round(font_scale * 2)))
        pad = max(4, int(round(6 * font_scale)))

        for pred in predictions:
            x, y, w, h = int(pred['x']), int(pred['y']), int(pred['width']), int(pred['height'])
            x1, y1, x2, y2 = int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + h / 2)

            color = (59, 166, 73)
            cv2.rectangle(image_combined, (x1, y1), (x2, y2), color, 2)

            label = f"{pred['confidence']:.1%}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            (label_w, label_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)

            text_y = y2 + label_h + pad
            if text_y > height - pad:
                text_y = max(label_h + pad, y1 - pad)

            text_x = max(0, x1)
            bg_x1 = max(0, x1 - pad)
            bg_y1 = max(0, text_y - label_h - pad)
            bg_x2 = min(width - 1, x1 + label_w + pad)
            bg_y2 = min(height - 1, text_y + baseline + pad)

            cv2.rectangle(image_combined, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
            cv2.putText(image_combined, label, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

        _, buffer = cv2.imencode('.jpg', image_combined)
        return Response(content=buffer.tobytes(), media_type="image/jpeg")

    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
