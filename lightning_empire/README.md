# Lightning Empire

This project contains a collection of tools and applications for the "Lightning Empire" ecosystem, including a banking notification system and a weather analysis tool for drivers.

## Project Structure

The project is organized into the following directories:

-   `notification_app/`: A Flask-based web application that listens for banking webhooks, processes transactions, and sends notifications.
-   `analysis/`: Contains scripts for data analysis, such as the weather analysis tool for driver safety.
-   `tests/`: Includes unit tests for the applications to ensure correctness and reliability.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd lightning_empire
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Applications

### Banking Notification Webhook

The banking notification app is a Flask server that listens for incoming transaction data.

1.  **Set Environment Variables:**
    The application requires environment variables for bank accounts and notification service tokens. You can set them in your shell or create a `.env` file in the root of the `lightning_empire` directory.

    Example `.env` file:
    ```
    BANK_CTBC_CODE="822"
    BANK_CTBC_ACCOUNT="484540302460"
    BANK_POST_CODE="700"
    BANK_POST_ACCOUNT="00210091602429"
    TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
    TELEGRAM_CHAT_ID="your_telegram_chat_id"
    LINE_NOTIFY_TOKEN="your_line_notify_token"
    ```
    *Note: The application uses `python-dotenv` to load these variables, which you may need to install (`pip install python-dotenv`) and import in `main.py` if you choose to use a `.env` file.*

2.  **Run the Flask server:**
    ```bash
    python notification_app/main.py
    ```
    The server will start on `http://0.0.0.0:5000`.

### Weather Analysis Script

The weather analysis script fetches and analyzes weather data to provide insights for drivers.

-   **Run the script:**
    ```bash
    python analysis/weather.py
    ```
    The script will print the analysis to the console, display a plot of the temperature data, and save the results to a CSV file.

## Running Tests

To ensure the application is working correctly, you can run the unit tests.

-   **Execute the test suite:**
    ```bash
    python -m unittest tests/test_app.py
    ```