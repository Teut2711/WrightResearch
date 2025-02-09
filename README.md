# README.md
NOTE: Put gmail username and "app" password(https://support.google.com/mail/answer/185833?hl=en)  to check mail subjects in logs
# FastAPI Application

This is a FastAPI application that serves as an example project.

## Project Structure

```
my-fastapi-app
├── app
│   ├── main.py          # Entry point of the FastAPI application
│   ├── database.py      # Database setup and utility functions
│   ├── fetch_emls.py    # Fetch emails and save as .eml files
│   ├── extract_trades.py # Extract trades from .eml files
│   ├── reconcile_trades.py # Reconcile trades
│   └── __init__.py      # Marks the app directory as a Python package
├── backend
│   ├── Dockerfile       # Instructions to build a Docker image
│   ├── requirements.txt # Lists the Python dependencies
│   └── README.md        # Documentation for the project
├── .env                 # Environment variables
├── .dockerignore        # Files and directories to ignore in Docker builds
├── docker-compose.yaml  # Docker Compose configuration
└── data                 # Directory to save .eml files and other data
```

## Requirements

To run this application, you need to have Python 3.7 or higher installed. You can install the required dependencies using:

```bash
pip install -r requirements.txt
```

## Running the Application

To run the FastAPI application, execute the following command:

```bash
uvicorn app.main:app --reload --port 8000
```

This will start the application in development mode, and you can access it at `http://127.0.0.1:8000`.

## Docker

To build and run the application using Docker, use the following commands:

1. Build and run the Docker container:

```bash
docker-compose up --build
```

This will start the application in development mode, and you can access it at `http://localhost:8000`.

## Environment Variables

The application uses environment variables for configuration. These variables are stored in a `.env` file in the root of the project. Here is an example of the `.env` file:

```properties
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=
IMAP_PASSWORD=
SAVE_DIR=data/emls
```

Make sure to replace the placeholder values with your actual credentials and settings.

## Accessing the Application

Once the application is running, you can access the API documentation at `http://localhost:8000/docs`.
