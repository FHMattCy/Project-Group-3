from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

coords_file = os.path.join(os.getcwd(), 'coords.txt')

@app.route('/')
def index():
    # หน้า index ที่ให้กรอก city กับ country
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    coords_message = f"Latitude: {latitude}, Longitude: {longitude}\n"
    with open(coords_file, 'w') as file:
        file.write(coords_message)

    return jsonify({
        "latitude": latitude,
        "longitude": longitude,
        "message": "Location received and saved to coords.txt"
    })

@app.route('/location', methods=['GET', 'POST'])
def enter_location():
    if request.method == 'POST':
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        if not latitude or not longitude:
            return render_template('location.html', error="Please enter both latitude and longitude.")

        coords_message = f"Latitude: {latitude}, Longitude: {longitude}\n"
        with open(coords_file, 'w') as file:
            file.write(coords_message)

        return render_template('location.html', success="Coordinates saved successfully!")

    return render_template('location.html')

if __name__ == '__main__':
    app.run(debug=True)
