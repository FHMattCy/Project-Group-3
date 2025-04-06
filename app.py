from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Ensure the coords.txt file is in the root project directory
coords_file = os.path.join(os.getcwd(), 'coords.txt')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_location():
    data = request.get_json()

    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    # Create a message to log the coordinates
    coords_message = f"Latitude: {latitude}, Longitude: {longitude}\n"

    # Write coordinates to the coords.txt file
    with open(coords_file, 'w') as file:
        file.write(coords_message)

    # Example: Return the coordinates and a success message
    prediction = {
        "latitude": latitude,
        "longitude": longitude,
        "message": "Location received and saved to coords.txt"
    }

    return jsonify(prediction)

if __name__ == '__main__':
    app.run(debug=True)
