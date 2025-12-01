# Arogya-NextGen

Arogya-NextGen is a comprehensive healthcare management system designed to provide patient health monitoring, medical information, and connect patients with healthcare services. The application supports multiple languages (English and Marathi) and includes features for both patients and pharmacy staff.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Running the Project](#running-the-project)

## Features

*   **Patient Management:** User registration, login, and profile management.
*   **Health Data Submission:** Patients can submit blood pressure and sugar readings via SMS using Twilio.
*   **Automated Alerts:** Health workers receive alerts for critical health readings (e.g., high BP, high sugar).
*   **Pharmacy Management:** Pharmacy staff can log in and manage medication inventory.
*   **AI Chatbot:** An integrated chatbot for user interaction and information.
*   **Doctor Search & Appointments:** Functionality to find doctors and schedule appointments.
*   **Service Information:** Details about available healthcare services.
*   **Testimonials:** A section for user feedback.
*   **Multi-language Support:** The application is designed to support multiple languages, with English and Marathi currently implemented.

## Technologies Used

### Backend

*   **Python:** The primary language for the backend logic.
*   **Flask:** A micro web framework for Python, used for routing, requests, and responses.
*   **SQLite3:** A C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine. It's used for the project's database.
*   **Twilio:** A communication platform used for sending and receiving SMS messages, specifically for health data submission and alerts.
*   **Werkzeug:** A comprehensive WSGI web application library, used here for password hashing.

### Frontend

*   **HTML5:** For structuring the web content.
*   **CSS3:** For styling the web pages.
*   **JavaScript:** For interactive elements and dynamic content.
*   **Bootstrap 5.3.3:** A popular CSS framework for developing responsive and mobile-first websites.
*   **Font Awesome 6.7.2:** A toolkit that provides scalable vector icons.
*   **Swiper:** A modern touch slider used for carousels or image galleries.
*   **jQuery:** A fast, small, and feature-rich JavaScript library, likely used by some of the included vendor libraries.

## Setup and Installation

Follow these steps to set up and run the project locally:

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd Arogya-NextGen
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
3.  **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
4.  **Install the Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Database Setup:**
    The project uses SQLite. A `health.db` file is expected. It's likely this database is created and populated on first run or there's a separate script for it. Ensure the database file exists or is created when the application starts.

6.  **Twilio Configuration:**
    *   Sign up for a [Twilio](https://www.twilio.com/) account.
    *   Obtain your `ACCOUNT_SID`, `AUTH_TOKEN`, and `TWILIO_PHONE_NUMBER`.
    *   Update these values in `app.py` (or ideally, use environment variables for production).
    *   Configure a Twilio webhook to point to your application's `/sms` endpoint.

## Running the Project

1.  **Activate your virtual environment:**
    *   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
2.  **Run the Flask application:**
    ```bash
    python app.py
    ```
    The application will typically be accessible at `http://127.0.0.1:5000/` in your web browser.


## Team Members
1. Sahil Shinde
2. Yogiraj Shinde
3. Pranav Patil 
4. Kartika Borse