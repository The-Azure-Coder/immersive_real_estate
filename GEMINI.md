# Gemini Guidelines for Code Generation – Immersive Real Estate API

This document defines strict guidelines for generating code for the Immersive Real Estate Platform backend. Follow these rules to ensure the code is correct, maintainable, secure, and production-ready.

---

## 1. General Principles

- **Modularity**: Organize code into logical modules (models, schemas, routers, services, core utilities). Follow the structure defined in the implementation plan.
- **Type Hints**: Use Python type hints for all function arguments and return values. Leverage Pydantic models for request/response validation.
- **Documentation**: Add docstrings to all public functions, classes, and modules. Keep comments concise but explanatory.
- **Error Handling**: Use explicit exception handling with appropriate HTTP status codes. Never expose internal error details to the client.
- **Logging**: Integrate logging for debugging and monitoring. Use `print()` only for temporary debugging; remove before final.

---

## 2. Code Style

- **PEP 8**: Follow standard Python style (use `black` or similar formatter).
- **Imports**: Group imports: standard library, third-party, local modules. Use absolute imports.
- **Naming**: 
  - Classes: `CamelCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
- **Line Length**: Max 100 characters.

---

## 3. Database and Models

- **SQLAlchemy Models**: Define models in `app/models/`. Use `Base` from `database.py`. 
  - Set `__tablename__` explicitly.
  - Use appropriate column types and constraints (e.g., `nullable=False`, `unique=True`).
  - Define relationships with `back_populates`.
- **Migrations**: Use Alembic. Generate migrations with `--autogenerate` after model changes. Test migrations locally.
- **Performance**: Add indexes for frequently queried fields. Use `selectinload` for relationships to avoid N+1 queries.

---

## 4. Pydantic Schemas

- Define in `app/schemas/` with clear naming: `*Base`, `*Create`, `*Out`, `*Update`.
- Use `from_attributes = True` in `Config` for ORM mode.
- Use `EmailStr` for emails, `constr` for validation if needed.
- Keep schemas consistent with models but avoid exposing sensitive fields (e.g., `hashed_password`).

---

## 5. API Endpoints (Routers)

- **Versioning**: All endpoints under `/api/v1/`.
- **HTTP Methods**: Follow REST conventions:
  - `GET` – retrieve resources
  - `POST` – create
  - `PUT` – full update
  - `PATCH` – partial update
  - `DELETE` – delete
- **Response Status Codes**: Use appropriate codes (200, 201, 204, 400, 401, 403, 404, 500).
- **Dependencies**: Use `Depends(get_db)` for database sessions. Protect endpoints with `Depends(get_current_user)` and role checks.

---

## 6. Authentication & Authorization

- **JWT**: Use `python-jose` for token creation/verification. Store tokens with expiration.
- **Password Hashing**: Use `passlib` with bcrypt.
- **Role-Based Access Control**: Implement `require_role(role)` dependency. Verify user role from token or database.
- **Security**: Never store plain passwords. Use environment variables for secrets.

---

## 7. Services Layer

- **Business Logic**: Place in `app/services/` (e.g., `nanobanana.py`, `storage.py`). Keep controllers thin.
- **External APIs**: Use `httpx` for async calls. Handle timeouts and retries.
- **Error Handling**: Catch exceptions, log them, and raise HTTP exceptions with appropriate messages (or re-raise for background tasks).

---

## 8. File Upload & Storage

- **Conditional Storage**: Implement both S3 and local storage as per `USE_S3` flag.
- **Local Storage**: Files saved under `settings.LOCAL_STORAGE_PATH`. Ensure directory exists. Return URL path that can be served via static files.
- **S3 Storage**: Use `boto3` with credentials from settings. Set bucket ACL to `public-read` or use presigned URLs.
- **Validation**: Check file size and type (images only: jpg, png, etc.). Use `python-multipart`.

---

## 9. Testing

- **Framework**: Use `pytest`, `pytest-asyncio`, `httpx`.
- **Test Database**: Use a separate test database (e.g., `realestate_test`). Override `get_db` dependency.
- **Coverage**: Aim for >80% coverage. Include unit and integration tests.
- **Mock External Services**: Mock S3, Nanobanana API calls in tests to avoid real network requests.
- **Test All Endpoints**: Include success and failure cases (e.g., unauthorized, not found).
- **Run Tests Before Commit**: Ensure all tests pass. Use pre-commit hooks if possible.

---

## 10. Configuration & Environment

- **Settings**: Use Pydantic `BaseSettings` with `.env` file. Validate required fields.
- **Secrets**: Never hardcode. Load from environment.
- **Environment-Specific**: Allow different configs for development, testing, production.

---

## 11. Error Responses

- **Consistent Format**: Return errors in JSON like `{"detail": "error message"}`.
- **HTTP Exceptions**: Use FastAPI's `HTTPException` with status codes.
- **Validation Errors**: Let FastAPI handle automatically (422).

---

## 12. Performance & Optimization

- **Async**: Use async endpoints for I/O-bound operations (DB, external API).
- **Database**: Use `await` with SQLAlchemy async? (Note: original plan uses sync SQLAlchemy; if using async, use `asyncpg` and `databases` or SQLAlchemy 1.4+ async. Stick to plan unless instructed otherwise.)
- **Background Tasks**: Use FastAPI `BackgroundTasks` or Celery for long-running jobs (e.g., 3D generation). Avoid blocking requests.

---

## 13. Documentation

- **OpenAPI**: FastAPI auto-generates docs. Add descriptions to endpoints, parameters, and schemas.
- **README**: Keep updated with setup, testing, and deployment instructions.
- **Postman Collection**: Provide a collection for manual testing (see separate guide).

---

## 14. Code Generation Checklist

Before delivering code, verify:
- [ ] No syntax errors.
- [ ] All imports exist and are correct.
- [ ] Type hints used.
- [ ] Functions have docstrings.
- [ ] Tests pass (simulate if needed).
- [ ] Environment variables are used correctly.
- [ ] No hardcoded secrets.
- [ ] Database migrations included if model changed.
- [ ] Error handling covers edge cases.
- [ ] Code follows the structure defined in the implementation plan.

---

By adhering to these guidelines, the generated code will be robust, testable, and ready for deployment.

---

# Changelog / Document of Changes

This document summarizes the modifications and enhancements made to the original implementation plan.

| **Date**       | **Change**                                                                                       | **Reason**                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| 2025-03-13     | Added conditional file storage: S3 or local based on `USE_S3` environment variable.               | Allows development without AWS credentials; simplifies local testing.                        |
| 2025-03-13     | Implemented static file serving for local uploads via FastAPI `StaticFiles`.                      | Enables access to locally stored images during development.                                  |
| 2025-03-13     | Enhanced models with proper relationships and fields (e.g., `created_at`, `is_active`).           | Improves data integrity and supports future features.                                        |
| 2025-03-13     | Added Pydantic schemas for all models with `from_attributes`.                                     | Ensures consistent serialization/deserialization.                                            |
| 2025-03-13     | Created role-based access control dependencies (`get_current_user`, `require_role`).               | Secures endpoints by user role.                                                              |
| 2025-03-13     | Integrated Nanobanana AI service with `httpx` async calls.                                        | Efficient external API communication.                                                         |
| 2025-03-13     | Wrote comprehensive tests for authentication, properties, and storage services.                   | Ensures reliability and catches regressions.                                                 |
| 2025-03-13     | Added environment configuration using Pydantic `BaseSettings`.                                    | Centralizes settings and improves security.                                                  |
| 2025-03-13     | Detailed API documentation for Postman testing (see separate guide).                              | Facilitates manual testing and frontend integration.                                         |
| 2025-03-13     | Provided Gemini guidelines for future code generation.                                            | Maintains consistency and quality in AI-assisted development.                                |

---

# API Testing Guide for Postman

This guide explains how to test the Immersive Real Estate API using Postman. All endpoints are prefixed with `/api/v1`.

## Prerequisites

- The API server is running locally at `http://localhost:8000`.
- A test database is set up (migrations applied).
- If using local storage, the `./uploads` directory is writable.

## 1. Authentication

### Register a User

- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/auth/register`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "email": "owner@test.com",
  "password": "secret123",
  "full_name": "John Doe",
  "role": "owner"
}
```
- **Expected Response**: `200 OK` with user details (excluding password).

### Login

- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/auth/login`
- **Headers**: `Content-Type: application/x-www-form-urlencoded`
- **Body** (form-data):
  - `username`: owner@test.com
  - `password`: secret123
- **Expected Response**: `200 OK` with `access_token` and `token_type`.

Copy the `access_token` – it will be used for authenticated requests.

## 2. Properties

### List Properties (Public)

- **Method**: `GET`
- **URL**: `http://localhost:8000/api/v1/properties/`
- **Headers**: None
- **Expected Response**: `200 OK` with an array of properties.

### Create a Property (Requires Authentication & Role "owner")

- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/properties/`
- **Headers**: 
  - `Authorization: Bearer <your_token>`
  - `Content-Type: multipart/form-data` (set automatically by Postman)
- **Body** (form-data):
  - `title`: "Cozy Cottage"
  - `location`: "Countryside"
  - `price`: 250000
  - `land_size`: 150
  - `image`: (select a local image file)
- **Expected Response**: `201 Created` with the created property, including `image_url` and `model_3d_url` (if generation succeeded).

### Get a Single Property

- **Method**: `GET`
- **URL**: `http://localhost:8000/api/v1/properties/{property_id}`
- **Headers**: None
- **Expected Response**: `200 OK` with property details, or `404 Not Found`.

### Update a Property (Owner or Admin Only)

- **Method**: `PUT`
- **URL**: `http://localhost:8000/api/v1/properties/{property_id}`
- **Headers**: `Authorization: Bearer <your_token>`, `Content-Type: application/json`
- **Body** (raw JSON):
```json
{
  "title": "Updated Cottage",
  "location": "Mountain View",
  "price": 275000,
  "land_size": 150
}
```
- **Expected Response**: `200 OK` with updated property.

### Delete a Property (Owner or Admin Only)

- **Method**: `DELETE`
- **URL**: `http://localhost:8000/api/v1/properties/{property_id}`
- **Headers**: `Authorization: Bearer <your_token>`
- **Expected Response**: `204 No Content`.

## 3. Professionals (Marketplace)

### Create Professional Profile (Requires Authentication)

- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/professionals/`
- **Headers**: `Authorization: Bearer <your_token>`, `Content-Type: application/json`
- **Body**:
```json
{
  "profession": "architect",
  "bio": "Experienced in modern designs.",
  "hourly_rate": 85
}
```
- **Expected Response**: `201 Created` with profile details.

### List Professionals

- **Method**: `GET`
- **URL**: `http://localhost:8000/api/v1/professionals/`
- **Expected Response**: `200 OK` array.

## 4. Testing with Different Roles

To test role-based access, register users with different roles (e.g., `buyer`, `architect`) and attempt to access restricted endpoints. For instance:
- A `buyer` should **not** be able to create properties (expect `403 Forbidden`).

## 5. Notes on File Storage

- **S3 Mode**: If `USE_S3=true` in `.env`, uploaded images will be stored in S3 and return public URLs.
- **Local Mode**: Files are saved locally under `./uploads`. The API serves them via `/uploads/...`. Ensure the static files mount is active (check `main.py`).

## 6. Error Handling

Common error responses:
- `400 Bad Request`: Validation error (e.g., missing field).
- `401 Unauthorized`: Missing or invalid token.
- `403 Forbidden`: Insufficient permissions.
- `404 Not Found`: Resource not found.
- `422 Unprocessable Entity`: Request body validation failed.

## 7. Automating with Postman

- Import the API schema from `http://localhost:8000/openapi.json` to auto-generate a collection.
- Set an environment variable `base_url` to `http://localhost:8000`.
- Create a pre-request script to automatically set the token after login, or manually copy it.

---

By following this guide, you can thoroughly test all API endpoints and verify the correct behavior of the Immersive Real Estate Platform backend.