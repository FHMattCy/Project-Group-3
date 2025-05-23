import os
from flask import Flask, render_template, request, jsonify
from fetchSolarIrradiance import fetchSolarIrradiance
from calculateEnergyOutput import calculate_energy_output_prediction

app = Flask(__name__)

coords_file = os.path.join(os.getcwd(), 'coords.txt')

@app.route('/')
def index():
    # TH - หน้า index ที่ให้กรอก city กับ country
    # EN - Index page where you enter city and country.
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

    fetchSolarIrradiance(latitude, longitude)
    calculate_energy_output_prediction()
    
    return jsonify({
        "latitude": latitude,
        "longitude": longitude,
        "message": "Location received and saved to coords.txt"
    })

# Entering Location manually linked to /location.html
@app.route('/location', methods=['GET', 'POST'])
def enter_location():
    if request.method == 'POST':
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        # Error preventing empty input.
        if not latitude or not longitude:
            return render_template(
                'location.html',
                error="Please enter both latitude and longitude.",
                latitude=latitude,
                longitude=longitude
            )
        # Error preventing out of range input.
        elif not (-90 <= int(latitude) <= 90) or not (-180 <= int(longitude) <= 180):
            return render_template(
                'location.html',
                error="Please input number between -90 to 90 for latitude and -180 to 180 for longitude."
            )

        coords_message = f"Latitude: {latitude}, Longitude: {longitude}\n"
        with open(coords_file, 'w') as file:
            file.write(coords_message)

        fetchSolarIrradiance(latitude, longitude)
        calculate_energy_output_prediction()

        return render_template(
            'location.html',
            success="Coordinates saved successfully!",
            latitude_display=latitude,
            longitude_display=longitude
        )


    # TH - Method GET — ลองอ่าน coords.txt ถ้ามี
    # EN - Method GET — Try to read coords.txt if there is one.
    lat, lon = None, None
    if os.path.exists(coords_file):
        with open(coords_file, 'r') as file:
            content = file.read().strip()
            try:
                # TH - แยกพิกัดจากข้อความในไฟล์
                # EN - Separate cords. from text in file.
                parts = content.replace("Latitude: ", "").replace("Longitude: ", "").split(',')
                lat = parts[0].strip()
                lon = parts[1].strip()
            except IndexError:
                pass  # TH - ถ้าอ่านไม่ได้ก็ไม่ต้องแสดง EN - Won't display if cannot read file.

    return render_template('location.html', latitude=lat, longitude=lon)

# Route to handle PV system configuration
@app.route('/submit_pv', methods=['POST'])
def submit_pv():
    data = request.get_json()

    area = data.get('area')
    panel_eff = data.get('panel_efficiency')
    inverter_eff = data.get('inverter_efficiency')

    # Write PV system configuration to file
    with open('pv_config.txt', 'w', encoding='utf-8') as f:
        f.write(f"Panel Area: {area}\n")
        f.write(f"Panel Efficiency: {panel_eff}\n")
        f.write(f"Inverter Efficiency: {inverter_eff}\n")

    return jsonify({"message": "PV system configuration saved successfully."})

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
