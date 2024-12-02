import streamlit as st
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import PIL.Image as Image
import os
import csv
import uuid
import logging
import json  # Import the json module

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load the model
try:
    model = load_model('final_model.h5')
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    st.error("Model could not be loaded.")
    st.stop()

# Absolute path to the CSV file
csv_file_path = os.path.abspath("predictions.csv")

# Create the CSV file with headers if it doesn't exist
if not os.path.exists(csv_file_path):
    with open(csv_file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Image Path', 'Predicted Class', 'Probabilities'])

# Class labels
class_labels = ['Leaf smut', 'Brown spot', 'Bacterial leaf blight']

def preprocess_image(image: np.ndarray) -> np.ndarray:
    # Resize and preprocess the image to match the model input
    image = cv2.resize(image, (224, 224))  # Change to 224x224
    image = image / 255.0  # Normalize to [0, 1] range
    image = np.expand_dims(image, axis=0)
    return image

def save_prediction(image, predicted_class, probabilities):
    # Save the image to a unique path
    image_dir = os.path.abspath("images")
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, f"{uuid.uuid4()}.jpg")
    cv2.imwrite(image_path, image)

    # Format probabilities with class names
    prob_dict = {class_labels[i]: f"{prob:.4f}" for i, prob in enumerate(probabilities)}
    prob_json = json.dumps(prob_dict)  # Convert probabilities to JSON string

    # Save prediction to CSV
    try:
        with open(csv_file_path, mode="a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([image_path, predicted_class, prob_json])
        logging.info(f"Prediction saved: {image_path}, {predicted_class}, {prob_json}")
    except Exception as e:
        logging.error(f"Error writing to CSV: {e}")
        st.error("Could not save prediction to CSV.")
    
    return image_path


st.title("Image Classification with TensorFlow")

uploaded_file = st.file_uploader("Choose an image...", type="jpg")

if uploaded_file is not None:
    try:
        # Load the image
        image = Image.open(uploaded_file)
        image_array = np.array(image)

        st.image(image, caption='Uploaded Image.', use_column_width=True)

        # Preprocess the image
        preprocessed_image = preprocess_image(image_array)

        # Make prediction
        prediction = model.predict(preprocessed_image)

        # Get the predicted class and probabilities
        predicted_class_idx = np.argmax(prediction, axis=1)[0]
        predicted_class = class_labels[predicted_class_idx]
        probabilities = prediction[0].tolist()  # Convert to list for JSON serialization

        # Save the prediction and the image
        image_path = save_prediction(image_array, predicted_class, probabilities)

        st.write(f"Predicted Class: {predicted_class}")
        st.write("Probabilities:")
        for i, prob in enumerate(probabilities):
            st.write(f"{class_labels[i]}: {prob:.4f}")

        st.write(f"Image saved at: {image_path}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        st.error("An error occurred during prediction.")
