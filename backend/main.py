from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from ultralytics import YOLO
import os
import uuid
import shutil
import cv2

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "uploaded_model.pt"
model = None

os.makedirs("outputs", exist_ok=True)

# -----------------------------------------------------------
# UPLOAD MODEL
# -----------------------------------------------------------
@app.post("/upload_model_local")
async def upload_model_local(file: UploadFile = File(...)):
    global model

    with open(MODEL_PATH, "wb") as f:
        shutil.copyfileobj(file.file, f)

    model = YOLO(MODEL_PATH)

    return {"message": "Model uploaded & loaded!"}


# -----------------------------------------------------------
# AUTO ANNOTATE IMAGE
# -----------------------------------------------------------
@app.post("/annotate_image")
async def annotate_image(file: UploadFile = File(...)):

    if model is None:
        return {"error": "Upload a YOLO model first!"}

    # Save input image
    image_id = str(uuid.uuid4())
    input_path = f"outputs/{image_id}.jpg"
    annot_path = f"outputs/{image_id}_annot.jpg"
    label_path = f"outputs/{image_id}.txt"

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # YOLO inference
    results = model(input_path)[0]

    img = cv2.imread(input_path)
    h, w = img.shape[:2]

    # Create YOLO label file
    with open(label_path, "w") as lf:
        for box in results.boxes:
            cls = int(box.cls[0])
            x1, y1, x2, y2 = box.xyxy[0]

            # YOLO format
            xc = float((x1 + x2) / 2 / w)
            yc = float((y1 + y2) / 2 / h)
            bw = float((x2 - x1) / w)
            bh = float((y2 - y1) / h)

            lf.write(f"{cls} {xc} {yc} {bw} {bh}\n")

            # Draw bounding box
            cv2.rectangle(img,
                          (int(x1), int(y1)),
                          (int(x2), int(y2)),
                          (0, 255, 0), 2)
            cv2.putText(img,
                        str(cls),
                        (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2)

    cv2.imwrite(annot_path, img)

    return {
        "message": "Annotated!",
        "annotated_image": f"/get_image/{image_id}_annot.jpg",
        "label_file": f"/get_label/{image_id}.txt"
    }


# -----------------------------------------------------------
# RETURN IMAGE FILE
# -----------------------------------------------------------
@app.get("/get_image/{name}")
async def get_image(name: str):
    return FileResponse(f"outputs/{name}")


# -----------------------------------------------------------
# RETURN LABEL FILE
# -----------------------------------------------------------
@app.get("/get_label/{name}")
async def get_label(name: str):
    return FileResponse(f"outputs/{name}")
