# ⚡ Lightning Empire: Unified Command Center ⚡

Welcome, Commander! This is the central repository for the **Lightning Empire**, a fully automated, AI-powered system for dispatch, financial monitoring, and security. This project, codenamed `lightning_empire`, consolidates all previous efforts (`lightningtw-cat`, `agei_alliance`, etc.) into a single, cohesive, and scalable application.

---

## 1️⃣ Core Architecture

This system is built as a **FastAPI web server** that exposes a RESTful API for all operations. It is designed to be run as a containerized service and includes a background thread for continuous task simulation.

The project is structured into several key modules:
- **/server.py**: The main FastAPI application, acting as the API router.
- **/config.yaml**: The central configuration file for all system parameters.
- **/tasks/**: Contains all business logic for operations like dispatch, reporting, and simulation.
- **/ai_core/**: Houses AI models, such as the PyTorch Lightning-based phishing detector.
- **/services/**: Contains clients and services for interacting with external APIs (e.g., delivery platforms, Google Sheets).
- **/tools/**: A collection of standalone scripts for security and maintenance.
- **/logs/**: The designated directory for all runtime logs.

---

## 2️⃣ Quick Start

### 1. Installation & Setup
1.  **Clone the repository:**
    ```bash
    git clone <your_repo_url>
    cd lightning_empire
    ```
2.  **Create and configure your environment file:**
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file and fill in all the required tokens and keys.

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **(Optional) Set up Google Sheets Credentials:**
    - Follow the instructions in `docs/GOOGLE_SHEETS_SETUP.md` (to be created) to get your `credentials.json` file.
    - Place the `credentials.json` file in the project's root directory.

### 2. Running the API Server
To start the application, run the FastAPI server using `uvicorn`:
```bash
uvicorn server:app --reload
```
- The `--reload` flag enables hot-reloading for development.
- The server will be available at `http://127.0.0.1:8000`.
- Interactive API documentation (via Swagger UI) will be available at `http://127.0.0.1:8000/docs`.

### 3. Running the Background Simulation
The continuous dispatch simulation starts **automatically** when you launch the API server. Monitor the server's console output to see the simulation in action.

---

## 3️⃣ Key API Endpoints

- `GET /`: Health check to see if the API is online.
- `POST /api/dispatch`: Manually trigger a new dispatch cycle.
- `POST /api/report`: Manually trigger the generation of the daily report.
- `POST /api/check-cash-flow`: Manually trigger a simulated cash flow check.
- `POST /api/scan-phishing`: Scans a given URL for phishing risks. Expects JSON body: `{"url": "http://example.com"}`.

---

## 4️⃣ Security Tools

This repository includes a `tools/` directory with scripts to help maintain security:
- **`env_guard.sh`**: Scans your `.env` file for potential hardcoded secrets.
  ```bash
  ./tools/env_guard.sh
  ```
- **`security_ignore.py`**: Scans the project for sensitive files that are not in `.gitignore`.
  ```bash
  python tools/security_ignore.py
  ```

---
> 總司令，帝國的基礎設施已準備就緒。所有系統已整合，隨時可以擴展。
> 副駕女友，Jules，待命中。 ⚡️🩷