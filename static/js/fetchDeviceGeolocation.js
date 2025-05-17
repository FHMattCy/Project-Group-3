document.addEventListener("DOMContentLoaded", () => {
    const useLocationBtn = document.getElementById("use-device-location");

    if (useLocationBtn) {
        useLocationBtn.addEventListener("click", (event) => {
            // Prevent form submission when clicking the "Use Device Location" button
            event.preventDefault();

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const latitude = position.coords.latitude;
                        const longitude = position.coords.longitude;

                        // Display on page
                        document.getElementById("latitude").textContent = latitude.toFixed(6);
                        document.getElementById("longitude").textContent = longitude.toFixed(6);

                        // Reuse sendToBackend function from script.js if available
                        if (typeof sendToBackend === "function") {
                            sendToBackend(latitude, longitude);
                        } else {
                            // Fallback: send manually
                            fetch('/predict', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ latitude, longitude })
                            })
                            .then(res => res.json())
                            .then(data => {
                                console.log("Device location submitted:", data);
                            })
                            .catch(err => {
                                console.error("Error submitting device location:", err);
                            });
                        }
                    },
                    (error) => {
                        console.error("Geolocation error:", error);
                        alert("Failed to get device location.");
                    }
                );
            } else {
                alert("Geolocation is not supported by your browser.");
            }
        });
    }
});
