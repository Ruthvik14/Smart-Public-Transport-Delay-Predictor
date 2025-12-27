# Smart Public Transport Delay Predictor (Connect Transit)

A real-time delay prediction system for Bloomington-Normal public transit, built with FastAPI, Next.js, and Machine Learning.

## Prerequisities

- **Docker Desktop**: Must be installed and running. [Download here](https://www.docker.com/products/docker-desktop/).
- **Git**: To clone/manage the repo.

## Quick Start

1.  **Start Docker Desktop** on your machine.
2.  Open a terminal in this project directory (`d:\Smart Public Transport Delay Predictor`).
3.  Run the following command to build and start all services:

    ```powershell
    docker-compose up --build
    ```

    *Note: This might take a few minutes the first time to download images and install dependencies.*

4.  Wait until you see logs indicating the services are ready (e.g., `Uvicorn running on...`, `database system is ready to accept connections`).

## Database Setup (First Time Only)

Once the containers are running, you need to initialize the database schema and load the static GTFS data.

1.  Open a **new** terminal window (keep the `docker-compose up` one running).
2.  Enter the Backend container:

    ```powershell
    docker-compose exec api bash
    ```

3.  Inside the container, generate and run migrations:

    ```bash
    # Create the initial migration file
    alembic revision --autogenerate -m "init_db"

    # Apply the migration to the database
    alembic upgrade head
    ```

4.  Load the Static GTFS Data (Routes, Stops, Schedules):

    ```bash
    python -m app.services.gtfs_loader
    ```

    *You should see output like "Loading routes...", "Inserting X stops...", etc.*

5.  (Optional) Exit the container:
    ```bash
    exit
    ```

## ML Model Training

To enable delay predictions, you need to train the initial model (using synthetic data for now):

1.  Enter the backend container (if not already inside):
    ```powershell
    docker-compose exec api bash
    ```

2.  Run the training pipeline:
    ```bash
    # Generate synthetic training data
    python ml/scripts/build_labels.py

    # Train the model
    python ml/scripts/train.py
    ```

## Accessing the Application

- **Web App (Frontend)**: [http://localhost:3000](http://localhost:3000)
- **API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Admin Dashboard**: [http://localhost:3000/admin](http://localhost:3000/admin)

## Troubleshooting

- **Docker Pipe Error**: If you see "The system cannot find the file specified", Docker Desktop is likely not running. Start it and try again.
- **Port Conflicts**: Ensure ports 3000 (Web), 8000 (API), and 5432 (Postgres) are free.
- **Data Not Showing**: Ensure you ran the `gtfs_loader` script.
