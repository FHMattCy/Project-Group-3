def calculate_power_output(G, A, n_pv, n_inv):
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


def calculate_energy_output(P, hours):
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


# Example values
G = 3  # Solar irradiance in W/m²
A = 50    # Panel area in m2
n_pv = 0.18  # Panel efficiency (18%)
n_inv = 0.95  # Inverter efficiency (95%)
sunlight_hours = 5  # Effective sunlight hours

# Calculate power output (in watts)
P = calculate_power_output(G, A, n_pv, n_inv)

# Calculate total energy output over the period (in kWh)
E = calculate_energy_output(P, sunlight_hours)

print(f"Instantaneous Power Output: {P} W")
print(f"Total Energy Output over {sunlight_hours} hours: {E:.2f} kWh")