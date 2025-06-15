import os
import pandas as pd
import csv
from flask import Flask, render_template, request, redirect, jsonify, session, send_file
from fetchSolarIrradiance import fetchSolarIrradiance
from calculateEnergyOutput import calculate_energy_output_prediction

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For using session

coords_file = os.path.join(os.getcwd(), 'coords.txt')

#main page
@app.route('/')
def index():
    # TH - หน้า index ที่ให้กรอก city กับ country
    # EN - Index page where you enter city and country.
    latitude = session.get('latitude')
    longitude = session.get('longitude')
    return render_template('index.html', latitude=latitude, longitude=longitude)

#Route for getting latitude and lonitude by input city and country name
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    with open(coords_file, 'w') as file:
        file.write(f"Latitude: {latitude}, Longitude: {longitude}\n")

    fetchSolarIrradiance(latitude, longitude)
    hourly_predictions = calculate_energy_output_prediction()

    # Ensure the directory exists
    os.makedirs(os.path.join('Project-Group-3', 'Data'), exist_ok=True)
    # Save predictions to HourOrderAndEstimated.csv 
    output_path = os.path.join('Project-Group-3','Data', 'HourOrderAndEstimated.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Hour', 'Estimated Energy'])  # kWh
        for hour, value in enumerate(hourly_predictions, start=1):
            writer.writerow([hour, round(value, 4)])

    return jsonify({"message": "Prediction completed successfully."}), 200

#Route for getting latitude and lonitude by manual
# Entering Location manually linked to /location.html

@app.route('/location', methods=['GET', 'POST'])
def manual_location():
    if request.method == 'POST':
        try:
            lat = float(request.form.get('latitude'))
            lon = float(request.form.get('longitude'))

            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return render_template('location.html', error='Coordinates out of range')

            # Save to session
            session['latitude'] = lat
            session['longitude'] = lon

            # Save to coords.txt file
            with open(coords_file, 'w') as file:
                file.write(f"Latitude: {lat}, Longitude: {lon}\n")

            # Recalculate irradiance and predictions
            fetchSolarIrradiance(lat, lon)
            hourly_predictions = calculate_energy_output_prediction()

            # Save prediction CSV file
            os.makedirs(os.path.join('Project-Group-3', 'Data'), exist_ok=True)
            output_path = os.path.join('Project-Group-3','Data', 'HourOrderAndEstimated.csv')
            with open(output_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Hour', 'Estimated Energy'])
                for hour, value in enumerate(hourly_predictions, start=1):
                    writer.writerow([hour, round(value, 4)])

            return redirect('/')  # redirect to homepage after saving and calculation
        except ValueError:
            return render_template('location.html', error='Invalid coordinate format')

    return render_template('location.html')


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

    # Recalculate predictions after PV config is saved
try:
    if os.path.exists(coords_file):
        with open(coords_file, 'r') as file:
            coords = file.read()
            parts = coords.replace("Latitude: ", "").replace("Longitude: ", "").split(',')
            latitude = float(parts[0].strip())
            longitude = float(parts[1].strip())

            # Fetch irradiance and recalculate energy output
            fetchSolarIrradiance(latitude, longitude)
            hourly_predictions = calculate_energy_output_prediction()

            output_path = os.path.join('Project-Group-3','Data', 'HourOrderAndEstimated.csv')
            with open(output_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Hour', 'Estimated Energy'])  # kWh
                for hour, value in enumerate(hourly_predictions, start=1):
                    writer.writerow([hour, round(value, 4)])
except Exception as e:
    print(f"[submit_pv] Error during recalculation: {str(e)}")



#Power Prediction Table
@app.route('/energy_data', methods=['GET'])
def get_energy_data():
    data = []
    try:
        file_path = os.path.join('Project-Group-3', 'Data', 'HourOrderAndEstimated.csv')
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            data.append({
                'Hour': int(row['Hour']),
                'Estimated_Energy': float(row['Estimated Energy'])
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data)

#Send HourOrderAndEstimated.csv to front end
@app.route('/HourOrderAndEstimated.csv')
def serve_estimated_csv():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'Data', 'HourOrderAndEstimated.csv')
    return send_file(file_path, mimetype='text/csv')

#Show the Total in the table
@app.route('/results')
def show_results():
    try:
        file_path = os.path.join('Project-Group-3', 'Data', 'HourOrderAndEstimated.csv')

        df = pd.read_csv(file_path)

        df['Estimated Energy (kWh)'] = df['Estimated Energy'] 

        energy_data = df[['Hour', 'Estimated Energy (kWh)']].to_dict(orient='records')
        total_energy = df['Estimated Energy (kWh)'].sum()
    except Exception as e:
        return render_template('error.html', message=str(e))

    return render_template('results.html', energy_data=energy_data, total_energy=round(total_energy, 2))

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
