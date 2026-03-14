# Immersive Real Estate API

This is a RESTful API for an immersive real estate platform, featuring 3D model generation and flexible file storage.

## Features
- User Authentication (JWT)
- Role-Based Access Control (Buyer, Owner, Admin, Professionals)
- Property Management with Image Uploads
- 3D Model Generation (via Nanobanana AI)
- Local or S3 File Storage

## Setup

1. **Clone the repository**
2. **Create a virtual environment and install dependencies:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   - Copy `.env.example` to `.env` and fill in your details.
   - You need a running **PostgreSQL** database.
   - You need a **Nanobanana API Key**.
   
   **IMPORTANT:** If you encounter issues with the `DATABASE_URL`, you may need to hardcode it in `app/core/config.py` and `alembic.ini`.

4. **Run database migrations:**
   To apply the initial migration and create the necessary tables, run:
   ```powershell
   .\venv\Scripts\alembic upgrade head
   ```

5. **Start the development server:**
   ```powershell
   uvicorn app.main:app --reload
   ```

## Creating New Migrations

When you change your SQLAlchemy models, you'll need to create a new migration script:
```powershell
.\venv\Scripts\alembic revision --autogenerate -m "A short message describing your changes"
```
Then, apply the new migration to your database:
```powershell
.\venv\Scripts\alembic upgrade head
```

## Testing

Run tests with `pytest`:
```powershell
$env:PYTHONPATH="."
.\venv\Scripts\pytest tests/ -v
```
Tests use a local SQLite database (`test.db`) for convenience and do not require PostgreSQL to be running.

## API Documentation
Once the server is running, visit:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Implementation Notes
- **Bcrypt compatibility**: `bcrypt` is pinned to `4.0.1` to ensure compatibility with `passlib`.
- **Pydantic V2**: The project uses Pydantic V2 schemas and settings.
- **SQLAlchemy 2.0**: The project uses modern SQLAlchemy 2.0 conventions.
