# Shared API Contract — TerraVision Hackathon
**Version 1.0 · March 2026**

This document serves as the single source of truth for the communication between the Next.js Frontend and FastAPI Backend.

---

## 1. Authentication

**Base URL:** `http://localhost:8000/api/v1`

### Register
`POST /auth/register`
- **Request:** `{ "email": "...", "password": "...", "full_name": "...", "role": "buyer | owner | architect | professional" }`
- **Response:** `201 Created` - `{ "id": 1, "email": "...", "full_name": "...", "role": "..." }`

### Login
`POST /auth/login`
- **Request:** `form-data` - `{ "username": "email", "password": "password" }`
- **Response:** `200 OK` - `{ "access_token": "...", "token_type": "bearer" }`

---

## 2. Properties

### List Properties
`GET /properties/`
- **Response:** `200 OK` - `Array<PropertyOut>` (Only approved properties)

### Create Property (Owner Only)
`POST /properties/`
- **Request:** `multipart/form-data`
    - `title`, `description`, `location`, `price`, `land_size`
    - `image`: Cover image
    - `image_front`, `image_back`, `image_left`, `image_right`: Multi-angle photos
- **Response:** `201 Created` - `PropertyOut`

### Get Property Details
`GET /properties/{id}`
- **Response:** `200 OK` - `PropertyOut`

### Check 3D Model Status (Polling)
`GET /properties/{id}/model-status`
- **Response:** `200 OK` - `{ "status": "pending | processing | complete | failed", "progress": 0-100, "model_url": "string | null" }`

---

## 3. Walkthrough & Config

### Get Walkthrough Config
`GET /properties/{id}/walkthrough-config`
- **Response:** `200 OK` - `{ "spawn_position": { "x": 0, "y": 1.7, "z": 0 }, "hotspots": [...], "model_scale": 1.0, "floor_count": 1 }`

---

## 4. Data Models (TypeScript Interfaces)

```typescript
interface PropertyOut {
  id: number;
  owner_id: number;
  title: string;
  description: string;
  location: string;
  price: number;
  land_size: number;
  image_url: string; // Cover photo
  images: Array<{ url: string; image_type: string }>;
  model_3d_url: string | null;
  model_3d_status: 'pending' | 'processing' | 'complete' | 'failed';
  is_model_generated: boolean;
  created_at: string;
}

interface WalkthroughConfig {
  spawn_position: { x: number; y: number; z: number };
  hotspots: Array<{
    label: string;
    position: { x: number; y: number; z: number };
    camera_direction: { x: number; y: number; z: number };
  }>;
  model_scale: number;
  floor_count: number;
}
```

---

## 5. Development Guidelines

1. **CORS:** Backend must allow `http://localhost:3000` (and `3001` if needed).
2. **Static Files:** All images and GLB models are served from `/uploads/`.
3. **Draco Compression:** Frontend must use `DRACOLoader` for `.glb` files.
4. **Auth Header:** `Authorization: Bearer <TOKEN>`
