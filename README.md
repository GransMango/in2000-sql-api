# in2000-weather-sqlapi

This is a Python Flask application that serves weather data from an SQL database, with caching and deployment to Azure Web App via GitHub Actions.

## Features

- Flask web application serving weather data
- Caching using Flask-Caching
- Deployment to Azure Web App using GitHub Actions
- Simple API to fetch all activities or a specific activity
- Example JSON response if cache is not available

## Prerequisites

- Python 3.10
- Azure Web App for deployment
- GitHub repository for CI/CD pipeline
- Environment variables configured for database connection and API key

## Setup

1. Clone the repository:
    
   ```sh
   git clone https://github.com/your-username/in2000-weather-sqlapi.git
   cd in2000-weather-sqlapi
    ```

2. Create a virtual environment and activate it:
    
   ```sh
   python -m venv venv
   source venv/bin/activate
    ```
3. Install dependencies:
    
   ```sh
   pip install -r requirements.txt
    ```
4. Create a `.env` file and set the required environment variables:
    
   ```env
   api_key_update=your_api_key
   SQLAZURECONNSTR_SQL_activity=your_connection_string
    ```
5. Run the application:
   
   ```sh
   python app.py
    ```
## Endpoints

- `GET /` - Renders the main page.
- `GET /api/activities` - Fetches all activities.
- `GET /api/activities/<int:activity_id>` - Fetches a specific activity by ID.
- `POST /db/updatecache` - Updates the activities cache. Requires `X-API-KEY` header.

## Deployment

This project uses GitHub Actions to build and deploy the application to Azure Web App.

### GitHub Actions Workflow

The GitHub Actions workflow is defined in `.github/workflows/main.yml`. It includes two jobs:

- `build`: Checks out the code, sets up Python, creates a virtual environment, installs dependencies, and uploads a zipped artifact for deployment.
- `deploy`: Downloads the artifact, unzips it, and deploys the application to Azure Web App using the specified publish profile.

### Deploying

The easiest way to deploy this project is by removing the GitHub actions workflow, creating an Azure Web App and link it up to this repository. 
This will automatically generate a GitHub actions file that will publish the API. You then setup the environment variables in the Azure Web App.

### Triggering Deployment

The deployment workflow triggers on push to the `master` branch or can be manually triggered via the GitHub Actions UI.
