from fastapi import FastAPI, UploadFile, File, HTTPException
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import os
import csv
import uuid
import logging

# Initialize FastAPI
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Absolute path to the CSV file
csv_file_path = os.path.abspath("predictions.csv")

# Create the CSV file with headers if it doesn't exist
if not os.path.exists(csv_file_path):
    with open(csv_file_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Image Path", "Predicted Class", "Probabilities"])

# Load the model
try:
    model = load_model("final_model.h5")
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    raise HTTPException(status_code=500, detail="Model could not be loaded.")

# Class labels
class_labels = ["Leaf smut", "Brown spot", "Bacterial leaf blight"]

def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Resize and preprocess the image to match the model input."""
    image = cv2.resize(image, (224, 224))  # Resize to 224x224
    image = image / 255.0  # Normalize to [0, 1] range
    image = np.expand_dims(image, axis=0)
    return image

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    try:
        # Read the image file
        image_data = await file.read()
        image = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        if image is None:
            logging.error("Uploaded image is not valid.")
            raise HTTPException(status_code=400, detail="Invalid image format.")

        # Preprocess the image
        preprocessed_image = preprocess_image(image)

        # Make prediction
        prediction = model.predict(preprocessed_image)

        # Get the predicted class and probabilities
        predicted_class_idx = np.argmax(prediction, axis=1)[0]
        predicted_class = class_labels[predicted_class_idx]
        probabilities = prediction[0].tolist()

        # Save the image to a unique path
        image_dir = os.path.abspath("images")
        os.makedirs(image_dir, exist_ok=True)
        image_path = os.path.join(image_dir, f"{uuid.uuid4()}.jpg")
        cv2.imwrite(image_path, image)

        # Save prediction to CSV
        with open(csv_file_path, mode="a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([image_path, predicted_class, probabilities])

        logging.info(f"Prediction saved: {image_path}, {predicted_class}, {probabilities}")

        return {"predicted_class": predicted_class, "probabilities": probabilities, "image_path": image_path}

    except Exception as e:
        logging.error(f"An error occurred during prediction: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during prediction.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
