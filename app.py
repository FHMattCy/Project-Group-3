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
            return render_template(
                'location.html',
                error="Please enter both latitude and longitude.",
                latitude=latitude,
                longitude=longitude
            )

        coords_message = f"Latitude: {latitude}, Longitude: {longitude}\n"
        with open(coords_file, 'w') as file:
            file.write(coords_message)

        return render_template(
            'location.html',
            success="Coordinates saved successfully!",
            latitude_display=latitude,
            longitude_display=longitude
        )


    # Method GET — ลองอ่าน coords.txt ถ้ามี
    lat, lon = None, None
    if os.path.exists(coords_file):
        with open(coords_file, 'r') as file:
            content = file.read().strip()
            try:
                # แยกพิกัดจากข้อความในไฟล์
                parts = content.replace("Latitude: ", "").replace("Longitude: ", "").split(',')
                lat = parts[0].strip()
                lon = parts[1].strip()
            except IndexError:
                pass  # ถ้าอ่านไม่ได้ก็ไม่ต้องแสดง

    return render_template('location.html', latitude=lat, longitude=lon)

if __name__ == '__main__':
    print("✅ Starting Flask app...")
    app.run(debug=True)