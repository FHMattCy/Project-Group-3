# Project-Group-3 - PredictiveVoltaic

## Background

In recent years, there has been steady growth in the renewable energy sector. Especially systems installed at end consumers' homes, such as heat pumps and photovoltaic (PV) systems, are more popular than ever before. These systems not only positively impact the climate but also guarantee independence and are often supported by additional funding.

While it is common for PV system owners to track the electricity they generate, using predictive technology to forecast future power availability is not as widespread. However, this data is incredibly useful: knowing ahead of time how much power will be available allows users to schedule activities like doing laundry or charging an electric car at the optimal time. In an era where storing electricity is one of the most challenging aspects of renewable energy, this is more important than ever.

## Solution Idea

To improve this situation, we propose developing a tool that predicts power generation based on open weather forecast data combined with user input parameters to characterize the PV setup (e.g., location, maximum power output, etc.). This tool will focus on short-term predictions, targeting the near future (hours to days) rather than long-term averages (e.g., expected yearly output).

By leveraging real-time weather data and specific details about the user's PV system, our solution aims to provide accurate and actionable forecasts. This will enable users to optimize their energy usage by scheduling activities like laundry or electric vehicle charging during periods of peak solar power generation. Additionally, the tool will be designed to be user-friendly and accessible, addressing the common issues of complexity and cost associated with existing solar forecasting solutions.

## Solution Technologies

- HTML, CSS, JavaScript to communicate with the end user via a webpage.
- Python to fetch data from a wearther forecast API and calculate prediction.

## Requirements

- 64-bit Python (tested with version 3.13.x)
- Python packages listed in requirements.txt (can be installed with commend "pip install -r requirements.txt")

## Launching Project Locally

- Execute "python app.py" in a terminal.
- The (local) server IP and port can be seen in the console (Example: "* Running on http://127.0.0.1:5000")
- Open this link in a browser to set position, PV settings and/or to get predictions.
