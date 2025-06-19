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
