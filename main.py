from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import io
import os
import uuid
from pdf2image import convert_from_bytes
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create and mount static directory
static_dir = "static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Load model
try:
    model = YOLO("weights.pt")
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    raise Exception(f"Failed to load model: {str(e)}")

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")
    # Validate file
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
        logger.error("Invalid file format")
        raise HTTPException(status_code=400, detail="Invalid file format. Use PNG, JPG, or PDF.")
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        logger.error("File size exceeds 10 MB")
        raise HTTPException(status_code=400, detail="File size exceeds 10 MB")

    # Process file
    try:
        if file.filename.lower().endswith('.pdf'):
            logger.info("Converting PDF to image")
            images = convert_from_bytes(file_bytes, dpi=150)
            img = np.array(images[0])  # First page
        else:
            logger.info("Processing image file")
            img = np.array(Image.open(io.BytesIO(file_bytes)))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    # Run inference
    try:
        logger.info("Running inference")
        results = model(img)[0]
    except Exception as e:
        logger.error(f"Inference error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

    # Extract detections
    detections = []
    for box in results.boxes:
        if box.conf < 0.30:
            continue
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        detections.append({
            "label": results.names[int(box.cls)],
            "confidence": float(box.conf),
            "bbox": [x1, y1, x2 - x1, y2 - y1]
        })
    logger.info(f"Found {len(detections)} detections")

    # Generate overlay image
    overlay = img.copy()
    for det in detections:
        x, y, w, h = det["bbox"]
        color = (0, 255, 0)
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, 2)
        cv2.putText(overlay, f"{det['label']} {det['confidence']:.2f}",
                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Save overlay
    overlay_filename = f"overlay_{uuid.uuid4()}.png"
    overlay_path = os.path.join(static_dir, overlay_filename)
    cv2.imwrite(overlay_path, overlay)
    logger.info(f"Overlay saved at {overlay_path}")

    return {
        "detections": detections,
        "image_url": f"/static/{overlay_filename}"
    }