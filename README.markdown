# Blueprint Symbol Detection

This project provides a FastAPI application to detect `evse`, `panel`, and `gfi` symbols in parking-garage blueprints (PNG, JPG, or PDF files). It includes a web-based UI for uploading files, viewing detection results, and downloading the overlay image with bounding boxes, as well as a REST API endpoint (`POST /detect`).

## Features
- **Web UI**: Upload blueprints and view detected symbols with bounding boxes.
- **Download Option**: Save the overlay image with detections.
- **API Endpoint**: Programmatically detect symbols via `POST /detect`.
- **YOLOv8 Model**: Uses a trained YOLOv8-nano model for efficient detection.
- **Deployment**: Hosted on Hugging Face Spaces for easy access.

## Setup

### Prerequisites
- Python 3.9
- Git
- Dependencies listed in `requirements.txt`

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/mr-Drot/blueprint-symbol-detector.git
   cd blueprint-symbol-detector
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI server locally:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 7860
   ```

### Local Testing
- **UI**: Open `http://localhost:7860/` in a browser, upload a file, and view/download results.
- **API**: Test the `/detect` endpoint:
  ```bash
  curl -X POST "http://localhost:7860/detect" -F "file=@data/images/E003.png"
  ```

## Deployed Application

The application is deployed on Hugging Face Spaces:
- **UI**: Visit [https://mr-drot-blueprint-symbol-detector.hf.space/](https://mr-drot-blueprint-symbol-detector.hf.space/) to upload files and download overlay images.
- **API Endpoint**: `POST https://mr-drot-blueprint-symbol-detector.hf.space/detect`

### Sample Request
```bash
curl -X POST "https://mr-drot-blueprint-symbol-detector.hf.space/detect" -F "file=@data/images/E003.png"
```

### Sample Response
```json
{
  "detections": [
    {
      "label": "evse",
      "confidence": 0.95,
      "bbox": [104, 81, 38, 38]
    },
    {
      "label": "panel",
      "confidence": 0.87,
      "bbox": [200, 150, 50, 50]
    }
  ],
  "image_url": "/static/overlay_<uuid>.png"
}
```

## Project Structure
```
blueprint-symbol-detector/
├── main.py              # FastAPI application
├── best.pt              # Trained YOLOv8 model
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration for Hugging Face Spaces
├── static/              # Static files (UI)
│   ├── index.html
│   └── .gitkeep
├── data/                # Sample data
│   ├── images/
│   │   ├── E003.png
│   │   └── E004.png
│   └── labels/
│       ├── E003.txt
│       └── E004.txt
├── classes.txt          # Class names
└── README.md            # This file
```

## Notes
- The model (`best.pt`) was trained on a small dataset and may require re-training for optimal performance. See the training log for metrics.
- The application supports files up to 10 MB and processes PDFs by converting the first page to an image.
- Inference runs on CPU and completes within 30 seconds.

## License
MIT License