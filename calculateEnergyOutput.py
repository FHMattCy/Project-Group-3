import csv
import os

#For reading solar_radiation_data.csv
def calculate_energy_output_prediction():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "Data", "solar_radiation_data.csv")
    """
    Generate a prediction for energy produced by a PV system over a period of time.
    Prints cumulative energy output hour by hour.
    Returns list of hourly energy outputs (not cumulative).
    """
    #Get PV config
    pv_data = []
    with open('pv_config.txt', 'r') as file:
        for line in file:
            parts = line.split(':')
            if len(parts) > 1:
                try:
                    value = float(parts[1].strip().split()[0])
                    pv_data.append(value)
                except ValueError:
                    print(f"Warning: Invalid value in line: {line.strip()}")

    if len(pv_data) < 3:
        raise ValueError("pv_config.txt Please input the value at least 1 value inverter")

    panel_area = pv_data[0]
    panel_efficiency = pv_data[1]
    converter_efficiency = pv_data[2]

    hourly_energies = []
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header

        for idx, row in enumerate(reader, start=1):
            G = float(row[1].strip())
            P = _calculate_power_output(G, panel_area, panel_efficiency, converter_efficiency)
            E = _calculate_energy_output(P, 1)  # Wh
            hourly_energies.append(E)
            E_kWh = E / 1000  # transfer Wh into kWh
            print(f"Hour {idx}: {E_kWh:.4f} kWh")

    total_energy_wh = sum(hourly_energies)
    total_energy_kwh = total_energy_wh / 1000
    print(f"Total Estimated Energy: {total_energy_wh:.2f} Wh ({total_energy_kwh:.2f} kWh)")

    return [e / 1000 for e in hourly_energies]

#Formula for calculate Solar irradiance
def _calculate_power_output(G, A, n_pv, n_inv):

    """
    Calculate the current power output from the solar system.

    Parameters:
    G (float): Solar irradiance in W/m²
    A (float): Panel area in m²
    n_pv (float): Panel efficiency
    n_inv (float): Inverter efficiency

    Returns:
    float: Current power output in watts (W)
    """
    P = G * A * n_pv * n_inv
    return P

def _calculate_energy_output(P, hours):
  
    """
    Calculate the total energy output over a period of time.

    Parameters:
    P (float): Power output in watts (W)
    hours (float): Time duration in hours 

    Returns:
    float: Total energy output in kilowatt-hours (kWh)
    """
    E = P * hours # Convert from watt-hours to kilowatt-hours later in app.py
    return E