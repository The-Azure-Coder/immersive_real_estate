# Immersive Real Estate API

This is a RESTful API for an immersive real estate platform, featuring 3D model generation and flexible file storage.

## Features
- **Better Auth Compatible Authentication**: Session-based auth compatible with [Better Auth](https://www.better-auth.com/).
- **Role-Based Access Control**: Buyer, Owner, Admin, Architects, Masons, etc.
- **Property Management**: Image uploads and 3D model generation (via Nanobanana AI).
- **Flexible Storage**: Support for Local or AWS S3 file storage.

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
   
4. **Seed the database:**
   To create the tables and populate the database with initial users, properties, and professionals:
   ```powershell
   .\venv\Scripts\python seed.py
   ```
   *Note: This script will drop existing tables and recreate them to match the new Better Auth schema.*

5. **Start the development server:**
   ```powershell
   uvicorn app.main:app --reload
   ```

## API Route Authentication Matrix

| Endpoint | Method | Authentication | Role Required | Description |
|----------|--------|----------------|---------------|-------------|
| `/api/v1/auth/register` | `POST` | Public | None | Register a new user and get initial session. |
| `/api/v1/auth/login` | `POST` | Public | None | Standard OAuth2 login (username/password). |
| `/api/v1/auth/me` | `GET` | **Authenticated** | None | Get current user profile details. |
| `/api/v1/auth/users` | `GET` | **Authenticated** | `admin` | List all users in the system. |
| `/api/v1/auth/logout` | `POST` | **Authenticated** | None | Clear session cookie and logout. |
| `/api/v1/properties/` | `GET` | Public | None | List all properties. |
| `/api/v1/properties/` | `POST` | **Authenticated** | `owner` / `admin` | Create a new property listing. |
| `/api/v1/properties/{id}` | `GET` | Public | None | Get specific property details. |
| `/api/v1/properties/{id}` | `PUT` | **Authenticated** | Owner / `admin` | Update a property listing. |
| `/api/v1/properties/{id}` | `DELETE` | **Authenticated** | Owner / `admin` | Delete a property listing. |
| `/api/v1/professionals/` | `GET` | Public | None | List all professional profiles. |

---

## API Response Structures

### 1. Registration Responses

#### Success Response (201 Created)
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "usr_123456789",
      "email": "john.doe@example.com",
      "username": "johndoe",
      "firstName": "John",
      "lastName": "Doe",
      "role": "user",
      "permissions": ["read:own_profile", "update:own_profile"],
      "createdAt": "2024-01-15T10:30:00Z",
      "updatedAt": "2024-01-15T10:30:00Z"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Validation Error (400 Bad Request)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Email is already registered",
        "code": "EMAIL_EXISTS"
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/auth/register"
}
```

### 2. Login Responses

#### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600,
    "tokenType": "Bearer",
    "user": {
      "id": "usr_123456789",
      "email": "john.doe@example.com",
      "username": "johndoe",
      "firstName": "John",
      "lastName": "Doe",
      "role": "admin",
      "permissions": [
        "read:users",
        "create:users",
        "update:users",
        "delete:users"
      ],
      "lastLogin": "2024-01-15T10:30:00Z"
    },
    "session": {
      "id": "sess_123456789",
      "createdAt": "2024-01-15T10:30:00Z"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Invalid Credentials (401 Unauthorized)
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. User Listing Responses

#### Paginated User List (200 OK)
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": "usr_123456789",
        "email": "john.doe@example.com",
        "username": "johndoe",
        "firstName": "John",
        "lastName": "Doe",
        "role": "admin",
        "status": "active",
        "createdAt": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "totalPages": 5,
      "totalUsers": 47,
      "hasNext": true,
      "hasPrev": false
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 4. Role-Based Access Control (RBAC) Responses

#### Access Denied (403 Forbidden)
```json
{
  "success": false,
  "error": {
    "code": "ACCESS_DENIED",
    "message": "Insufficient permissions to perform this action",
    "requiredPermissions": ["user:delete"],
    "userPermissions": ["user:read", "user:update"],
    "resource": "/api/v1/auth/users",
    "action": "DELETE"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/v1/auth/users"
}
```

### 5. Logout Responses

#### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Logged out successfully",
  "data": {
    "sessionId": "sess_123456789",
    "terminatedAt": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## How to Test in Postman

We have provided a Postman collection: `immersive_real_estate.postman_collection.json`.

1. **Import the collection**: Open Postman, click "Import", and select the JSON file.
2. **Login**: Open the **Login** request. Body contains default admin credentials.
3. **Automatic Token Handling**: Upon login, the "Tests" script automatically saves the `access_token` to the `{{session_token}}` variable.
4. **Access Protected Routes**: Protected routes use the `{{session_token}}` variable as a Bearer token.

### Seeded Users
| Email | Password | Role |
|-------|----------|------|
| admin@example.com | adminpassword | admin |
| owner1@example.com | password123 | owner |
| architect1@example.com | password123 | architect |
| mason1@example.com | password123 | mason |
