from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import DetrForObjectDetection, DetrImageProcessor, DetrConfig
from safetensors.torch import safe_open
from PIL import Image, ImageDraw
import torch
import io
import base64
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter app
# Download model files if not present
download_models.download_models()

# Define model directory
MODEL_DIR = os.path.join(os.path.dirname(__file__), "detr_model")

# Load model and processor
config = DetrConfig.from_json_file(os.path.join(MODEL_DIR, "config.json"))
model = DetrForObjectDetection(config)
with safe_open(os.path.join(MODEL_DIR, "model.safetensors"), framework="pt", device="cpu") as f:
    state_dict = {k: f.get_tensor(k) for k in f.keys()}
model.load_state_dict(state_dict)
model.eval()
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")

def mask_predictions(image, boxes, fill_color=(0, 0, 0)):
    masked_image = image.copy()
    draw = ImageDraw.Draw(masked_image)
    for box in boxes:
        xmin, ymin, xmax, ymax = box.tolist()
        draw.rectangle([xmin, ymin, xmax, ymax], fill=fill_color)
    return masked_image

@app.route("/")
def health_check():
    return jsonify({"message": "DETR Flask Server is running"})

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    try:
        # Load and preprocess image
        image = Image.open(file.stream).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        
        # Run inference
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Postprocess outputs
        target_sizes = torch.tensor([image.size[::-1]])  # [height, width]
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]
        
        # Generate masked image
        masked_image = mask_predictions(image, results["boxes"])
        
        # Convert masked image to base64
        buffered = io.BytesIO()
        masked_image.save(buffered, format="PNG")
        masked_image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Prepare response
        response = {
            "boxes": results["boxes"].tolist(),
            "labels": [model.config.id2label.get(label.item(), f"Class {label.item()}") for label in results["labels"]],
            "scores": results["scores"].tolist(),
            "masked_image": f"data:image/png;base64,{masked_image_base64}"
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))