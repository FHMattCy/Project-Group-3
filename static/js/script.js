import './fetchDeviceGeolocation.js';  // Import the file with the browser geolocation api code

const apiKey = '78de0611a6abb6e3bae85ee67bacdc62'; // Replace with your OpenWeatherMap API key

// Input City and Country for latitude and lonitude
document.getElementById('location-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const city = document.getElementById('city').value;
    const country = document.getElementById('country').value;

    //Fetching Latitude and Longtitude from API.
    fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city},${country}&appid=${apiKey}`)
        .then(response => response.json())
        .then(data => {
            if (data.cod === 200) {
                const latitude = data.coord.lat;
                const longitude = data.coord.lon;

                document.getElementById('latitude').textContent = latitude;
                document.getElementById('longitude').textContent = longitude;

                sendToBackend(latitude, longitude);
            } else {
                alert("City not found. Please check the city name and country.");
            }
        })
        .catch(error => {
            console.error("Error fetching data:", error);
            alert("Error fetching the location data.");
        });
});

function sendToBackend(latitude, longitude) {
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            latitude: latitude,
            longitude: longitude
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log("Data received from backend:", data);
            // Loading new table after getting new cordinates
            loadPredictionPeriodTable();
            loadEstimatedOutputTable();
        })
        .catch(error => {
            console.error("Error sending data to backend:", error);
        });
}

document.getElementById('time-period-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const warningElement = document.getElementById('time-period-form-warning');
    warningElement.textContent = '';

    const start = document.getElementById('start-date-time').value.trim();
    const end = document.getElementById('end-date-time').value.trim();

    const startDateTime = new Date(start);
    const endDateTime = new Date(end);
    const currentDateTime = new Date();

    if (isNaN(startDateTime.getTime()) || isNaN(endDateTime.getTime())) {
        warningElement.textContent = 'Invalid date/time format. Use ISO like: 2025-06-01T00:00';
        return;
    }

    function addHours(date, hours) {
        return new Date(date.getTime() + hours * 60 * 60 * 1000);
    }

    if (!startDateTime && endDateTime) {
        if (endDateTime > currentDateTime) {
            // endDateTime in future, set startDateTime = now
            startDateTime = currentDateTime;
            start = startDateTime.toISOString().slice(0,16); // format as yyyy-MM-ddTHH:mm
        } else {
            // endDateTime in past, startDateTime = 24h before endDateTime
            startDateTime = addHours(endDateTime, -24);
            start = startDateTime.toISOString().slice(0,16);
        }
    } else if (!startDateTime && !endDateTime) {
        // both empty, start=now, end=24h later
        startDateTime = currentDateTime;
        endDateTime = addHours(currentDateTime, 24);
        start = startDateTime.toISOString().slice(0,16);
        end = endDateTime.toISOString().slice(0,16);
    } else if (startDateTime && !endDateTime) {
        // start present, end empty -> end = 24h after start
        endDateTime = addHours(startDateTime, 24);
        end = endDateTime.toISOString().slice(0,16);
    }

    if (startDateTime >= endDateTime) {
        warningElement.textContent = 'Start time must be before end time.';
        return;
    }

    // Get current lat/lon from UI
    const latitude = parseFloat(document.getElementById('latitude').textContent);
    const longitude = parseFloat(document.getElementById('longitude').textContent);

    if (isNaN(latitude) || isNaN(longitude)) {
        warningElement.textContent = 'Latitude and longitude are not set. Please select a location first.';
        return;
    }

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                latitude: latitude,
                longitude: longitude,
                start_datetime: start,
                end_datetime: end
            })
        });

        const data = await response.json();
        if (data.error) {
            warningElement.textContent = data.reason || 'Error during prediction.';
        } else {
            console.log('Prediction success:', data);
        }
    } catch (err) {
        warningElement.textContent = 'Failed to fetch prediction: ' + err.message;
        console.error(err);
    }
});


// PV system form submission
document.getElementById('pv-form').addEventListener('submit', function (e) {
    e.preventDefault();

    // Constants
    const area = parseFloat(document.getElementById('area').value);
    const panelEff = parseFloat(document.getElementById('panel-eff').value);
    const inverterEff = parseFloat(document.getElementById('inverter-eff').value);

    // Check input ranges
    const isValid = area >= 0.01 && panelEff >= 0.01 && panelEff <= 1 && inverterEff >= 0.01 && inverterEff <= 1;

    if (!isValid) {
        document.getElementById('response-message').innerText = 'Input is invalid value(s)';
        return;
    }


    // Try to look for an invalid values.
    try {
        if (!areaBetween(area, 0.01) && !between(panelEff, 0.01, 1) && !between(inverterEff, 0.01, 1)) throw "invalid value(s)."; //Check for values out of bounds then throw an error.

        if (areaBetween(area, 0.01) && between(panelEff, 0.01, 1) && between(inverterEff, 0.01, 1)) {
            //Summit form if all values are in range.
            fetch('/submit_pv', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    area: area,
                    panel_efficiency: panelEff,
                    inverter_efficiency: inverterEff
                    })
                })
                .then(res => res.json())
                .then(data => {
                    document.getElementById('response-message').innerText = data.message;
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('response-message').innerText = 'An error occurred.';
                });
        }
    // Catch and show error.
    } catch(error) {
        console.error('Error:', error)
        document.getElementById('response-message').innerText = 'Input is ' + error;

    // Submit only if valid
    fetch('/submit_pv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            area: area,
            panel_efficiency: panelEff,
            inverter_efficiency: inverterEff
        })
    })
        .then(res => res.json())
        .then(data => {
            document.getElementById('response-message').innerText = data.message;

        // Get current lat/lon shown on page
        const lat = document.getElementById('latitude').textContent;
        const lon = document.getElementById('longitude').textContent; 
    });
};

// Prepare to save Estimated Outout in the table
fetch('/energy_data')
    .then(response => response.json())
    .then(data => {
        let tbody = document.querySelector('#energy-table tbody');
        let total = 0;

        // Function that transfer hour into "HH:00-HH+1:00"
        function hourToPeriod(hour) {
            let start = (hour + 21) % 24; // shift to 22:00 = hour 1
            let end = (start + 1) % 24;
            return `${String(start).padStart(2, '0')}:00-${String(end).padStart(2, '0')}:00`;
        }

        data.forEach(row => {
            const energyWh = row['Estimated_Energy'];
            const energyKWh = energyWh / 1000;
            total += energyKWh;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${hourToPeriod(row['Hour'])}</td>
                <td>${energyKWh.toFixed(2)}</td>
            `;
            tbody.appendChild(tr);
        });

        document.getElementById('total-energy').innerHTML = `<strong>${total.toFixed(2)}</strong>`;
    })
    .catch(error => {
        console.error("Failed to load energy data:", error);
    });

// Prediction Peroid
function loadEstimatedOutputTable() {
    fetch('/HourOrderAndEstimated.csv')
        .then(response => response.text())
        .then(csvText => {
            const lines = csvText.trim().split('\n');
            const tableBody = document.querySelector('#energy-table tbody');
            const totalCell = document.getElementById('total-energy');
            tableBody.innerHTML = ''; // clear old data first

            let totalEnergyWh = 0;

            lines.slice(1).forEach((line) => { // skip header
                const [sessionLabel, energy] = line.split(',');

                const tr = document.createElement('tr');
                const tdSession = document.createElement('td');
                const tdEnergy = document.createElement('td');

                const energyWh = parseFloat(energy.trim());

                const hourInt = parseInt(sessionLabel.trim());
                const startHour = (21 + hourInt) % 24;  // start at 22:00 for hour = 1
                const endHour = (startHour + 1) % 24;
                const startStr = startHour.toString().padStart(2, '0') + ":00";
                const endStr = endHour.toString().padStart(2, '0') + ":00";
                tdSession.textContent = `${startStr}-${endStr}`;
                tdEnergy.textContent = (energyWh).toFixed(3); // show as kWh

                tr.appendChild(tdSession);
                tr.appendChild(tdEnergy);
                tableBody.appendChild(tr);

                totalEnergyWh += energyWh;
            });

            if (totalCell) {
                totalCell.textContent = (totalEnergyWh).toFixed(3); // kWh
            }
        })
        .catch(error => {
            console.error('Error loading energy data:', error);
        });
}

// Estimated Output data
function loadPredictionPeriodTable() {
    fetch('/solar_radiation_data.csv')
        .then(response => response.text())
        .then(csvText => {
            const rows = csvText.trim().split('\n').slice(1); // skip header
            const tableBody = document.querySelector('#energy-table tbody');
            tableBody.innerHTML = ''; // clear first

            rows.forEach((row) => {
                const [dateStr, radiation] = row.split(',');

                // Split time from dateStr and transfer to form "HH:mm"
                // Example of dateStr: "2025-05-19 22:00:00+00:00"
                const timePart = dateStr.split(' ')[1];  // "22:00:00+00:00"
                const hourMin = timePart.substring(0, 5); // "22:00"

                const tr = document.createElement('tr');

                const timeCell = document.createElement('td');
                const radiationCell = document.createElement('td');

                timeCell.textContent = hourMin;
                radiationCell.textContent = parseFloat(radiation).toFixed(2);

                tr.appendChild(timeCell);
                tr.appendChild(radiationCell);
                tableBody.appendChild(tr);
            });
        });
}

window.addEventListener('load', () => {
    loadPredictionPeriodTable();
    loadEstimatedOutputTable();
})});