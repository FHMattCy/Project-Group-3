import './fetchDeviceGeolocation.js';  // Import the file with the browser geolocation api code

const apiKey = '78de0611a6abb6e3bae85ee67bacdc62'; // Replace with your OpenWeatherMap API key

//Latitude and Longtitude input.
document.getElementById('location-form').addEventListener('submit', function(event) {
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
    })
    .catch(error => {
        console.error("Error sending data to backend:", error);
    });
}

// PV system form submission
document.getElementById('pv-form').addEventListener('submit', function (e) {
    e.preventDefault();

    // Constants
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
    }
});