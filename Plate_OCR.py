import os
from inference_sdk import InferenceHTTPClient
import statistics

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="8J273dpEvB21M7DwGsgY"
)

def is_double_line_plate(predictions, image_height):
    # Calculate the vertical center of the image
    image_center_y = image_height / 2
    
    # Calculate the vertical offsets from the image center
    offsets = [abs(pred['y'] - image_center_y) for pred in predictions]
    
    # Calculate the average offset
    avg_offset = statistics.mean(offsets)
    
    # Calculate the average height of the predictions
    avg_height = statistics.mean([pred['height'] for pred in predictions])
    
    # If the average offset is greater than a fraction of the average height, 
    # consider it a double line plate
    return avg_offset > 0.5 * avg_height

def arrange_predictions(predictions, image_height):
    if not is_double_line_plate(predictions, image_height):
        # Single line plate: sort by x-coordinate only
        return sorted(predictions, key=lambda pred: pred['x'])
    
    # Double line plate: separate into top and bottom rows
    image_center_y = image_height / 2
    top_row = []
    bottom_row = []
    
    for pred in predictions:
        if pred['y'] < image_center_y:
            top_row.append(pred)
        else:
            bottom_row.append(pred)
    
    # Sort each row by x-coordinate
    top_row = sorted(top_row, key=lambda pred: pred['x'])
    bottom_row = sorted(bottom_row, key=lambda pred: pred['x'])
    
    return top_row + bottom_row

def process_image(image_path):
    result = CLIENT.infer(image_path, model_id="dheeraj/2")
    
    # Extract image height from the result
    image_height = result.get('image', {}).get('height', 0)
    
    arranged_predictions = arrange_predictions(result['predictions'], image_height)
    
    plate_string = ''.join([pred['class'] for pred in arranged_predictions])
    
    return plate_string

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            image_path = os.path.join(folder_path, filename)
            result = process_image(image_path)
            print(f"Image: {filename}, Result: {result}")

# Specify the folder path containing the images
folder_path = r'C:\Users\Administrator\Downloads\archive\output'

# Process all images in the folder
process_folder(folder_path)
