import csv

def calculate_energy_output_prediction():
    """
    Generate a prediction for energy produced by a PV system over a period of time.

    PV settings are read from a file (pv_config.txt)
    solar radiation is read from a file (solar_radiation_data_csv)
        the expected granularity is per hour, so each entry represents one hour (timespan is CSV rows * hours)

    Returns:
    float: Total energy output in kilowatt-hours (kWh)
    """
    
    # get PV config
    pv_data = []

    with open('pv_config.txt', 'r') as file:
        for line in file:
            parts = line.split(':')
            if (len(parts) > 1):
                value = float(parts[1].strip())
                pv_data.append(value)
    
    panel_area = pv_data[0]
    panel_efficiency = pv_data[1]
    converter_efficiency = pv_data[2]


    # calculate prediction
    energy_prediction = 0.0
    ctr = 0
    
    with open('solar_radiation_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if (len(row) > 1) and ctr > 0:
                print(row[1])
                energy_prediction += _calculate_energy_output(_calculate_power_output(float(row[1].strip()), panel_area, panel_efficiency, converter_efficiency), 1)
            ctr = ctr + 1
    
    
    # log prediction to sonsole and return value
    print(f"Prediction over {ctr - 1} hours: {energy_prediction:.2f} kWh") # ctr - 1 because the fist csv line is only text...
    return energy_prediction


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
    E = P * hours / 1000  # Convert from watt-hours to kilowatt-hours
    return E