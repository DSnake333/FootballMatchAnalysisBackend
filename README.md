# Football Match Analysis Backend

This is the backend for the Football Match Analysis application, built using FastAPI. It processes match statistics from [FBRef](https://fbref.com/) and generates various visualizations using Plotly.

## Features
- Accepts a match URL from FBRef and processes player and team statistics.
- Generates interactive visualizations for different match metrics, including possession, defense, passing, and shooting.
- Uses subprocesses to run Python scripts for scraping and analysis.
- Supports CORS to communicate with the frontend.

## Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn
- Required Python libraries (install using `requirements.txt`)

## Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/DSnake333/FootballMatchAnalysisBackend.git
   cd FootballMatchAnalysisBackend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Backend
Start the FastAPI server using Uvicorn:
```bash
uvicorn app:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

## API Endpoints
### 1. Analyze Match
**Endpoint:**
```http
POST /analyze-match
```
**Request Body:**
```json
{
  "url": "https://fbref.com/..."
}
```
**Response:**
```json
{
  "message": "Match analysis completed successfully",
  "metrics": { ... }
}
```

### 2. Get Metrics
**Endpoint:**
```http
GET /visualizations/metrics
```
Returns JSON data containing match metrics and generated visualizations.

## Frontend Repository
The frontend for this project is available at:
[FootballMatchAnalysisFrontend](https://github.com/DSnake333/FootballMatchAnalysisFrontend)

## License
This project is licensed under the MIT License.
