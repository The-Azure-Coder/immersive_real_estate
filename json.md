# API Response Configuration Guide

## Authentication & Authorization API Responses

This guide provides standardized JSON response structures for authentication, registration, user listing, and role-based access control (RBAC) systems.

---

## Table of Contents
1. [Registration Responses](#1-registration-responses)
2. [Login Responses](#2-login-responses)
3. [User Listing Responses](#3-user-listing-responses)
4. [Role-Based Access Control (RBAC) Responses](#4-role-based-access-control-rbac-responses)
5. [Token Management](#5-token-management)
6. [Logout Responses](#6-logout-responses)
7. [Error Codes Reference](#7-error-codes-reference)

---

## 1. Registration Responses

### Success Response (201 Created)
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

### Validation Error (400 Bad Request)
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
      },
      {
        "field": "password",
        "message": "Password must be at least 8 characters long",
        "code": "INVALID_PASSWORD"
      },
      {
        "field": "username",
        "message": "Username can only contain letters, numbers, and underscores",
        "code": "INVALID_USERNAME"
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/auth/register"
}
```

---

## 2. Login Responses

### Success Response (200 OK)
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
        "delete:users",
        "read:roles",
        "manage:roles"
      ],
      "avatar": "https://example.com/avatars/johndoe.jpg",
      "lastLogin": "2024-01-15T10:30:00Z",
      "twoFactorEnabled": false
    },
    "session": {
      "id": "sess_123456789",
      "device": "Chrome on Windows",
      "ip": "192.168.1.100",
      "createdAt": "2024-01-15T10:30:00Z"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Two-Factor Required (200 OK with 2FA flag)
```json
{
  "success": true,
  "message": "2FA verification required",
  "data": {
    "requiresTwoFactor": true,
    "tempToken": "temp_2fa_123456789",
    "expiresIn": 300,
    "methods": ["google_authenticator", "sms", "email"],
    "user": {
      "id": "usr_123456789",
      "email": "john.doe@example.com",
      "username": "johndoe"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Invalid Credentials (401 Unauthorized)
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "remainingAttempts": 3,
    "lockoutTime": null
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Account Locked (403 Forbidden)
```json
{
  "success": false,
  "error": {
    "code": "ACCOUNT_LOCKED",
    "message": "Account temporarily locked due to multiple failed attempts",
    "lockedUntil": "2024-01-15T10:35:00Z",
    "remainingTime": 300
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 3. User Listing Responses

### Paginated User List (200 OK)
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
        "permissions": ["read:users", "write:users"],
        "status": "active",
        "lastActive": "2024-01-15T09:30:00Z",
        "createdAt": "2024-01-01T00:00:00Z",
        "profile": {
          "avatar": "https://example.com/avatars/johndoe.jpg",
          "department": "Engineering",
          "title": "Senior Developer"
        }
      },
      {
        "id": "usr_987654321",
        "email": "jane.smith@example.com",
        "username": "janesmith",
        "firstName": "Jane",
        "lastName": "Smith",
        "role": "user",
        "permissions": ["read:own_profile"],
        "status": "active",
        "lastActive": "2024-01-14T15:20:00Z",
        "createdAt": "2024-01-02T00:00:00Z",
        "profile": {
          "avatar": null,
          "department": "Marketing",
          "title": "Marketing Specialist"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "totalPages": 5,
      "totalUsers": 47,
      "hasNext": true,
      "hasPrev": false,
      "nextPage": 2,
      "prevPage": null
    },
    "filters": {
      "role": "all",
      "status": "active",
      "search": null
    },
    "sort": {
      "field": "createdAt",
      "order": "desc"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Single User Details (200 OK)
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_123456789",
      "email": "john.doe@example.com",
      "username": "johndoe",
      "firstName": "John",
      "lastName": "Doe",
      "role": "admin",
      "permissions": ["read:users", "write:users", "delete:users"],
      "status": "active",
      "lastLogin": "2024-01-15T09:30:00Z",
      "lastActive": "2024-01-15T09:30:00Z",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-15T09:30:00Z",
      "profile": {
        "avatar": "https://example.com/avatars/johndoe.jpg",
        "department": "Engineering",
        "title": "Senior Developer",
        "phone": "+1234567890",
        "location": "New York, USA"
      },
      "twoFactorEnabled": true,
      "sessions": [
        {
          "id": "sess_123",
          "device": "Chrome on Windows",
          "ip": "192.168.1.100",
          "lastActive": "2024-01-15T09:30:00Z"
        }
      ]
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 4. Role-Based Access Control (RBAC) Responses

### Role List (200 OK)
```json
{
  "success": true,
  "data": {
    "roles": [
      {
        "id": "role_admin",
        "name": "Administrator",
        "description": "Full system access",
        "permissions": [
          "user:create",
          "user:read",
          "user:update",
          "user:delete",
          "role:manage",
          "permission:assign",
          "system:configure"
        ],
        "usersCount": 3,
        "isSystem": true,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z"
      },
      {
        "id": "role_manager",
        "name": "Manager",
        "description": "Department management access",
        "permissions": [
          "user:read",
          "user:update",
          "reports:view",
          "reports:export"
        ],
        "usersCount": 12,
        "isSystem": false,
        "createdAt": "2024-01-02T00:00:00Z",
        "updatedAt": "2024-01-10T00:00:00Z"
      },
      {
        "id": "role_user",
        "name": "Regular User",
        "description": "Standard user access",
        "permissions": [
          "profile:read",
          "profile:update"
        ],
        "usersCount": 32,
        "isSystem": true,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Single Role Details (200 OK)
```json
{
  "success": true,
  "data": {
    "role": {
      "id": "role_manager",
      "name": "Manager",
      "description": "Department management access",
      "permissions": [
        {
          "id": "perm_user_read",
          "name": "Read Users",
          "resource": "user",
          "action": "read",
          "description": "Can view user details"
        },
        {
          "id": "perm_user_update",
          "name": "Update Users",
          "resource": "user",
          "action": "update",
          "description": "Can update user information"
        },
        {
          "id": "perm_reports_view",
          "name": "View Reports",
          "resource": "reports",
          "action": "view",
          "description": "Can view reports"
        }
      ],
      "users": [
        {
          "id": "usr_123",
          "name": "John Doe",
          "email": "john@example.com",
          "assignedAt": "2024-01-10T00:00:00Z"
        }
      ],
      "metadata": {
        "isSystem": false,
        "createdBy": "usr_admin_123",
        "createdAt": "2024-01-02T00:00:00Z",
        "updatedAt": "2024-01-10T00:00:00Z"
      }
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### User Role Assignment (200 OK)
```json
{
  "success": true,
  "message": "Role assigned successfully",
  "data": {
    "userId": "usr_123456789",
    "role": {
      "id": "role_manager",
      "name": "Manager",
      "permissions": [
        "user:read",
        "user:update",
        "reports:view",
        "reports:export"
      ]
    },
    "assignedBy": "usr_admin_123",
    "assignedAt": "2024-01-15T10:30:00Z",
    "expiresAt": null,
    "metadata": {
      "reason": "Department promotion",
      "department": "Engineering"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Permission Check (200 OK)
```json
{
  "success": true,
  "data": {
    "userId": "usr_123456789",
    "permissions": {
      "user:create": true,
      "user:read": true,
      "user:update": false,
      "user:delete": false,
      "reports:view": true,
      "reports:export": true
    },
    "roles": ["admin", "manager"],
    "inheritedFrom": {
      "user:create": "role_admin",
      "user:read": "role_admin",
      "reports:view": "role_manager",
      "reports:export": "role_manager"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Access Denied (403 Forbidden)
```json
{
  "success": false,
  "error": {
    "code": "ACCESS_DENIED",
    "message": "Insufficient permissions to perform this action",
    "requiredPermissions": ["user:delete"],
    "userPermissions": ["user:read", "user:update"],
    "resource": "/api/users/987654321",
    "action": "DELETE"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/users/987654321"
}
```

### Permission List (200 OK)
```json
{
  "success": true,
  "data": {
    "permissions": [
      {
        "id": "perm_user_create",
        "name": "Create Users",
        "resource": "user",
        "action": "create",
        "category": "User Management",
        "description": "Ability to create new users"
      },
      {
        "id": "perm_user_read",
        "name": "Read Users",
        "resource": "user",
        "action": "read",
        "category": "User Management",
        "description": "Ability to view user information"
      },
      {
        "id": "perm_reports_export",
        "name": "Export Reports",
        "resource": "reports",
        "action": "export",
        "category": "Reports",
        "description": "Ability to export reports"
      }
    ],
    "groupedBy": {
      "User Management": ["perm_user_create", "perm_user_read"],
      "Reports": ["perm_reports_export"]
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 5. Token Management

### Refresh Token Response (200 OK)
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600,
    "tokenType": "Bearer"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Token Validation Response (200 OK)
```json
{
  "success": true,
  "data": {
    "valid": true,
    "userId": "usr_123456789",
    "expiresAt": "2024-01-15T11:30:00Z",
    "issuedAt": "2024-01-15T10:30:00Z",
    "scopes": ["read:profile", "write:profile"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Token Expired (401 Unauthorized)
```json
{
  "success": false,
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "Access token has expired",
    "expiredAt": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:35:00Z"
}
```

---

## 6. Logout Responses

### Success Response (200 OK)
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

### Logout All Devices (200 OK)
```json
{
  "success": true,
  "message": "Logged out from all devices successfully",
  "data": {
    "terminatedSessions": 3,
    "terminatedAt": "2024-01-15T10:30:00Z",
    "devices": [
      {
        "sessionId": "sess_123",
        "device": "Chrome on Windows",
        "ip": "192.168.1.100",
        "lastActive": "2024-01-15T09:30:00Z"
      },
      {
        "sessionId": "sess_456",
        "device": "Mobile App on iOS",
        "ip": "192.168.1.101",
        "lastActive": "2024-01-14T22:15:00Z"
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 7. Error Codes Reference

### Authentication Errors (4xx)

| Code | HTTP Status | Description |
|------|------------|-------------|
| `INVALID_CREDENTIALS` | 401 | Email or password is incorrect |
| `ACCOUNT_LOCKED` | 403 | Account temporarily locked due to multiple failed attempts |
| `TOKEN_EXPIRED` | 401 | Access token has expired |
| `TOKEN_INVALID` | 401 | Token is malformed or invalid |
| `REFRESH_TOKEN_EXPIRED` | 401 | Refresh token has expired |
| `REFRESH_TOKEN_INVALID` | 401 | Refresh token is invalid |
| `2FA_REQUIRED` | 200 | Two-factor authentication required |
| `2FA_INVALID` | 401 | Invalid 2FA code |
| `SESSION_EXPIRED` | 401 | Session has expired |

### Registration Errors (4xx)

| Code | HTTP Status | Description |
|------|------------|-------------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `EMAIL_EXISTS` | 400 | Email is already registered |
| `USERNAME_EXISTS` | 400 | Username is already taken |
| `INVALID_PASSWORD` | 400 | Password does not meet requirements |
| `INVALID_EMAIL` | 400 | Email format is invalid |
| `INVALID_USERNAME` | 400 | Username contains invalid characters |

### Authorization Errors (4xx)

| Code | HTTP Status | Description |
|------|------------|-------------|
| `ACCESS_DENIED` | 403 | Insufficient permissions |
| `ROLE_NOT_FOUND` | 404 | Specified role does not exist |
| `PERMISSION_NOT_FOUND` | 404 | Specified permission does not exist |
| `ROLE_ALREADY_ASSIGNED` | 400 | User already has this role |
| `CANNOT_MODIFY_SYSTEM_ROLE` | 403 | Cannot modify system-defined roles |
| `INSUFFICIENT_PERMISSIONS` | 403 | Missing required permissions |

### User Management Errors (4xx)

| Code | HTTP Status | Description |
|------|------------|-------------|
| `USER_NOT_FOUND` | 404 | User does not exist |
| `USER_INACTIVE` | 403 | User account is inactive |
| `USER_SUSPENDED` | 403 | User account is suspended |
| `CANNOT_DELETE_SELF` | 403 | Cannot delete your own account |
| `CANNOT_MODIFY_SELF_ROLE` | 403 | Cannot modify your own role |

### Server Errors (5xx)

| Code | HTTP Status | Description |
|------|------------|-------------|
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `AUTH_SERVICE_UNAVAILABLE` | 503 | Authentication service unavailable |
| `TOKEN_GENERATION_FAILED` | 500 | Failed to generate token |

---

## Response Format Guidelines

### Success Response Structure
```json
{
  "success": true,
  "message": "Optional success message",
  "data": {}, // Response data object
  "timestamp": "2024-01-15T10:30:00Z" // ISO 8601
}
```

### Error Response Structure
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": [] // Optional additional details
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/endpoint" // Optional request path
}
```

### Pagination Metadata Structure
```json
{
  "pagination": {
    "page": 1,
    "limit": 10,
    "totalPages": 5,
    "totalItems": 47,
    "hasNext": true,
    "hasPrev": false,
    "nextPage": 2,
    "prevPage": null
  }
}
```

---

## HTTP Status Codes Summary

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful GET, PUT, PATCH requests |
| 201 | Created | Successful POST (registration, creation) |
| 400 | Bad Request | Validation errors, invalid input |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists |
| 429 | Too Many Requests | Rate limiting |
| 500 | Internal Server Error | Server-side error |

---

This documentation provides a comprehensive set of API response structures for authentication and authorization systems. Customize the field names and structures according to your specific requirements while maintaining consistency across all endpoints.