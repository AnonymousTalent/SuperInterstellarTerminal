import os
import threading
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables from .env file first
load_dotenv()

# Import project modules from the new structure
from tasks import dispatch, reporting, simulation
from ai_core import security
from services import api_client, financial_services # Add financial_services

# Check for required environment variables at startup
required_vars = ["REPORT_BOT_TOKEN", "COMMAND_BOT_TOKEN", "TELEGRAM_CHAT_ID", "DELIVERY_PLATFORM_API_KEY"]
for var in required_vars:
    if not os.getenv(var):
        print(f"❌ FATAL ERROR: Missing required environment variable: {var}")
        exit(1)

# Initialize FastAPI App
app = FastAPI(
    title="⚡ Lightning Empire: Unified API v3.0 ⚡",
    description="The unified backend API for the Lightning Empire, providing services for dispatch, reporting, financial monitoring, and security.",
    version="3.0.0"
)

# --- Background Task ---
@app.on_event("startup")
def startup_event():
    """On server startup, start the dispatch simulation in a background thread."""
    simulation_thread = threading.Thread(target=simulation.start_dispatch_simulation, daemon=True)
    simulation_thread.start()

# --- Pydantic Models for Request Bodies ---
class PhishingScanRequest(BaseModel):
    url: str

# --- API Endpoints ---

@app.get("/", tags=["System"])
def read_root():
    """Root endpoint to check if the API is online."""
    return {"message": "⚡ Lightning Empire API is online! ⚡"}

@app.post("/api/dispatch", tags=["Operations"])
def dispatch_orders_endpoint():
    """Triggers the system to fetch new orders from the delivery platform API."""
    try:
        return dispatch.run_dispatch()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/report", tags=["Operations"])
def generate_report_endpoint():
    """Generates the daily report and sends it to Telegram."""
    try:
        return reporting.run_daily_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check-cash-flow", tags=["Finance"])
def check_cash_flow_endpoint():
    """Runs a simulation of the financial services module to check cash flow."""
    try:
        return reporting.run_cash_flow_check()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scan-phishing", tags=["Security"])
def scan_for_phishing_endpoint(request: PhishingScanRequest):
    """Scans a given URL for phishing risks using the AI model."""
    try:
        detector = security.PhishingDetector()
        mock_features = security.get_mock_features()
        prediction = detector.predict_url(mock_features)
        return {"status": "completed", "url": request.url, "prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))