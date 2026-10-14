# Climate Hazard Trend Analyzer

## About the Project

Climate Hazard Trend Analyzer is a web application that shows how heatwaves, heavy rainfall, and droughts have changed over the years in different locations.

Users can select a state, city, or location using latitude and longitude. The application displays yearly data, charts, and insights to help understand climate trends.

## Features

* Select a state and city to analyze climate data.
* Choose a hazard: heatwave, heavy rainfall, or drought.
* Select a time range for analysis.
* View yearly data, events, and charts.
* Check whether climate trends are increasing or decreasing.
* Download results as CSV files.
* Store and reuse data to reduce repeated API calls.

## Tech Stack

* **Frontend:** React, JavaScript, Vite, Ant Design, Chart.js, Leaflet
* **Backend:** Python, FastAPI, Pandas, NumPy, SciPy
* **Database:** MongoDB
* **Weather Data:** Open-Meteo API
* **Testing:** Pytest

## Project Structure

```text
climate-hazard-trend-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── hazards/
│   │   ├── processing/
│   │   ├── repositories/
│   │   └── main.py
│   └── tests/
├── frontend/
│   └── src/
│       ├── pages/
│       ├── features/
│       ├── hooks/
│       ├── services/
│       └── components/
└── README.md
```

## How It Works

1. The user selects a location, hazard, and time range.
2. The backend checks MongoDB for existing data.
3. If the data is not available, it fetches weather data from Open-Meteo.
4. The backend processes the data and identifies climate events.
5. It calculates trends and generates insights.
6. The results are stored in MongoDB and sent to the frontend.
7. The frontend displays tables, charts, and insights.

## Getting Started

### Requirements

* Python 3.11 or later
* Node.js 18 or later

### 1. Start the Backend

Open a terminal and run:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
copy .env.example .env
python -m uvicorn app.main:app --reload
```

Backend API: http://localhost:8000

API documentation: http://localhost:8000/docs

### 2. Start the Frontend

Open another terminal and run:

```powershell
cd frontend
copy .env.example .env
npm install
npm start
```

Frontend URL: http://localhost:5173

## Main API Endpoints

| Method | Endpoint                  | Purpose                 |
| ------ | ------------------------- | ----------------------- |
| GET    | `/api/v1/health`          | Check backend status    |
| GET    | `/api/v1/regions`         | Get states or cities    |
| GET    | `/api/v1/regions/search`  | Search for a location   |
| GET    | `/api/v1/analysis`        | Get climate analysis    |
| GET    | `/api/v1/analysis/export` | Download results as CSV |

## Running Tests

To run the backend integration tests:

```powershell
cd backend
python -m pip install -r requirements-dev.txt
python -m pytest -m integration
```

These tests check the API using sample data and fake external services.

## Deployment

* **Database:** MongoDB Atlas
* **Backend:** Render
* **Frontend:** Vercel or Netlify

Configure the required environment variables before deploying the application.

## Limitations

* State analysis uses one grid point near the state's centre, not the entire state.
* Weather data comes from ERA5 and may not match local weather station readings.
* Heatwave analysis uses temperature and does not include humidity.
* Drought analysis is based on rainfall data.
* The analysis uses a fixed 1991–2020 baseline.

## Future Improvements

* Improve state-level analysis using multiple grid points.
* Add more climate indicators.
* Improve performance for large requests.
* Add frontend and end-to-end tests.
* Support PDF report downloads.

## AI Tools

Claude was used to help generate the initial code. The application was then run, reviewed, and updated to understand its structure and functionality.