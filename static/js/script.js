const apiKey = '78de0611a6abb6e3bae85ee67bacdc62'; // Replace with your OpenWeatherMap API key

document.getElementById('location-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const city = document.getElementById('city').value;
    const country = document.getElementById('country').value;

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
        loadRadiationTable();  
    })
    .catch(error => {
        console.error("Error sending data to backend:", error);
    });
}

// PV system form submission
document.getElementById('pv-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const area = parseFloat(document.getElementById('area').value);
    const panelEff = parseFloat(document.getElementById('panel-eff').value);
    const inverterEff = parseFloat(document.getElementById('inverter-eff').value);

    // Range Check functions
    //Regular range check functions.
    function between(x, min, max) {
        return x >= min && x <= max;
    }
    //Area range check function.
    function areaBetween(x, min) {
        return x >= min;
    }

    // Try to look for an invalid values.
    try {
        if (areaBetween(area, 0.01) == false && between(panelEff, 0.01, 1) == false && between(inverterEff, 0.01, 1) == false) throw "invalid value(s)."; //Note: Temporary fixes, It prevents invalid values from being saved to file, but only show error when area input box is given invalid input and not other boxes.
    // Catch and show error.
    } catch(err) {
        document.getElementById('response-message').innerText = 'Input is ' + err;
    // finally run the code.
    } finally {
        // checks if all values are in range.
        if (areaBetween(area, 0.01) == true && between(panelEff, 0.01, 1) == true && between(inverterEff, 0.01, 1) == true) { // Redundent, but when I removed it while testing, it stop preventing invalid input from being saved to file.
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
    }
});

// getting information from solar_radiation_data.csv to the table
fetch('/solar_radiation_data.csv')
    .then(response => response.text())
    .then(csv => {
        const rows = csv.trim().split('\n').slice(1); // get header off
        const tbody = document.querySelector('#radiation-table tbody');
        
        rows.forEach(row => {
            const [datetimeRaw, radiationRaw] = row.split(',');

            // cleaning information
            const datetime = new Date(datetimeRaw.trim());
            const radiation = parseFloat(radiationRaw.trim());

            const tr = document.createElement('tr');
            const tdDate = document.createElement('td');
            const tdRad = document.createElement('td');

            // Format date and time as readable (UTC)
            if (!isNaN(datetime.getTime())) {
                tdDate.textContent = datetime.toLocaleString('en-GB', {
                    timeZone: 'UTC',
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: false
                });
            } else {
                tdDate.textContent = "Invalid date";
            }

            // Format radiation
            if (!isNaN(radiation)) {
                tdRad.textContent = radiation.toFixed(2);
            } else {
                tdRad.textContent = "NaN";
            }

            tr.appendChild(tdDate);
            tr.appendChild(tdRad);
            tbody.appendChild(tr);
        });
    })
    .catch(error => {
        console.error('Error loading CSV:', error);
    });

function loadRadiationTable() {
    fetch('/solar_radiation_data.csv')
        .then(response => response.text())
        .then(csvText => {
            const rows = csvText.trim().split('\n').slice(1); //skip header
            const tableBody = document.querySelector('#radiation-table tbody');
            tableBody.innerHTML = ''; // clear first

            rows.forEach(row => {
                const [date, radiation] = row.split(',');
                const tr = document.createElement('tr');

                const dateCell = document.createElement('td');
                const radiationCell = document.createElement('td');

                dateCell.textContent = new Date(date).toLocaleString('en-GB', {
                    timeZone: 'UTC',
                    hour: '2-digit',
                    minute: '2-digit',
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                });

                radiationCell.textContent = parseFloat(radiation).toFixed(2);

                tr.appendChild(dateCell);
                tr.appendChild(radiationCell);
                tableBody.appendChild(tr);
            });
        });
}

window.onload = () => {
    loadRadiationTable();
};
