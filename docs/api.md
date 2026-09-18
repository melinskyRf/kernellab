# REST API Reference

Kernel Lab exposes a REST API via FastAPI. The API server starts with `kernellab server`.

**Base URL:** `http://127.0.0.1:8000`

**Interactive Documentation:**
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI spec: `http://127.0.0.1:8000/openapi.json`

---

## Health

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200` — Server is healthy

---

## Labs

### `POST /api/v1/labs`

Create a new lab.

**Request Body:**
```json
{
  "name": "my-driver-test",
  "provider": "fake",
  "machine": {
    "architecture": "x86_64",
    "cpus": 4,
    "memory": "4G"
  },
  "kernel": {
    "version": "6.12"
  },
  "tests": [
    {
      "name": "smoke-test",
      "command": "echo hello"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my-driver-test",
  "provider": "fake",
  "status": "created",
  "machine": {
    "architecture": "x86_64",
    "cpus": 4,
    "memory": "4G"
  },
  "kernel": {
    "version": "6.12"
  },
  "tests": [
    {
      "name": "smoke-test",
      "command": "echo hello"
    }
  ],
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Status Codes:**
- `201` — Lab created
- `400` — Invalid configuration
- `409` — Lab with same name already exists

---

### `GET /api/v1/labs`

List all labs.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `status` | string | — | Filter by status |
| `limit` | integer | 50 | Maximum results |
| `offset` | integer | 0 | Pagination offset |

**Response (200 OK):**
```json
{
  "labs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "my-driver-test",
      "provider": "fake",
      "status": "created",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

---

### `GET /api/v1/labs/{lab_id}`

Get lab details.

**Path Parameters:**
| Parameter | Type | Description |
|---|---|---|
| `lab_id` | string | Lab UUID |

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my-driver-test",
  "provider": "fake",
  "status": "created",
  "machine": {
    "architecture": "x86_64",
    "cpus": 4,
    "memory": "4G"
  },
  "kernel": {
    "version": "6.12"
  },
  "tests": [
    {
      "name": "smoke-test",
      "command": "echo hello"
    }
  ],
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200` — Lab found
- `404` — Lab not found

---

### `DELETE /api/v1/labs/{lab_id}`

Delete a lab and its associated jobs.

**Path Parameters:**
| Parameter | Type | Description |
|---|---|---|
| `lab_id` | string | Lab UUID |

**Response (204 No Content)**

**Status Codes:**
- `204` — Lab deleted
- `404` — Lab not found

---

### `POST /api/v1/labs/{lab_id}/run`

Run a lab (create a new job and execute).

**Path Parameters:**
| Parameter | Type | Description |
|---|---|---|
| `lab_id` | string | Lab UUID |

**Response (202 Accepted):**
```json
{
  "job_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "pending"
}
```

**Status Codes:**
- `202` — Job created and queued
- `404` — Lab not found
- `409` — Lab is already running

---

## Jobs

### `GET /api/v1/jobs`

List all jobs.

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `lab_id` | string | — | Filter by lab |
| `status` | string | — | Filter by status |
| `limit` | integer | 50 | Maximum results |
| `offset` | integer | 0 | Pagination offset |

**Response (200 OK):**
```json
{
  "jobs": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "lab_id": "550e8400-e29b-41d4-a716-446655440000",
      "type": "run",
      "status": "completed",
      "created_at": "2025-01-15T10:30:00Z",
      "started_at": "2025-01-15T10:30:01Z",
      "completed_at": "2025-01-15T10:30:05Z"
    }
  ],
  "total": 1
}
```

---

### `GET /api/v1/jobs/{job_id}`

Get job details.

**Path Parameters:**
| Parameter | Type | Description |
|---|---|---|
| `job_id` | string | Job UUID |

**Response (200 OK):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "lab_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "run",
  "status": "completed",
  "created_at": "2025-01-15T10:30:00Z",
  "started_at": "2025-01-15T10:30:01Z",
  "completed_at": "2025-01-15T10:30:05Z",
  "error": null,
  "artifacts": [
    {
      "id": "art-001",
      "name": "console.log",
      "path": "artifacts/660e8400/console.log",
      "size": 1024
    }
  ]
}
```

**Status Codes:**
- `200` — Job found
- `404` — Job not found

---

### `POST /api/v1/jobs/{job_id}/cancel`

Cancel a running job.

**Path Parameters:**
| Parameter | Type | Description |
|---|---|---|
| `job_id` | string | Job UUID |

**Response (200 OK):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "cancelled"
}
```

**Status Codes:**
- `200` — Job cancelled
- `404` — Job not found
- `409` — Job is not running

---

## Logs

### `GET /api/v1/jobs/{job_id}/logs`

Get logs for a job.

**Path Parameters:**
| Parameter | Type | Description |
|---|---|---|
| `job_id` | string | Job UUID |

**Query Parameters:**
| Parameter | Type | Default | Description |
|---|---|---|---|
| `type` | string | `all` | Log type (`all`, `console`, `stdout`, `stderr`) |
| `tail` | integer | — | Return only last N lines |

**Response (200 OK):**
```json
{
  "job_id": "660e8400-e29b-41d4-a716-446655440001",
  "logs": "[  0.000000] Linux version 6.12.0 (gcc version 13.2.0)\n[  0.000000] Command line: console=ttyS0\n..."
}
```

---

## Artifacts

### `GET /api/v1/jobs/{job_id}/artifacts`

List artifacts for a job.

**Path Parameters:**
| Parameter | Type | Description |
|---|---|---|
| `job_id` | string | Job UUID |

**Response (200 OK):**
```json
{
  "artifacts": [
    {
      "id": "art-001",
      "name": "console.log",
      "path": "artifacts/660e8400/console.log",
      "size": 1024,
      "created_at": "2025-01-15T10:30:05Z"
    },
    {
      "id": "art-002",
      "name": "dmesg.log",
      "path": "artifacts/660e8400/dmesg.log",
      "size": 2048,
      "created_at": "2025-01-15T10:30:05Z"
    }
  ]
}
```

---

### `GET /api/v1/jobs/{job_id}/artifacts/{artifact_id}`

Download an artifact.

**Path Parameters:**
| Parameter | Type | Description |
|---|---|---|
| `job_id` | string | Job UUID |
| `artifact_id` | string | Artifact UUID |

**Response (200 OK):**
- Content-Type: `application/octet-stream`
- Body: File content

**Status Codes:**
- `200` — Artifact returned
- `404` — Artifact not found

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

**Common Status Codes:**
- `400` — Bad request / validation error
- `404` — Resource not found
- `409` — Conflict (e.g., lab already running)
- `422` — Unprocessable entity (validation error)
- `500` — Internal server error

---

## Example: Complete Workflow

```bash
# 1. Create a lab
curl -X POST http://127.0.0.1:8000/api/v1/labs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-driver-test",
    "provider": "fake",
    "tests": [{"name": "hello", "command": "echo hello"}]
  }'

# 2. Run the lab
curl -X POST http://127.0.0.1:8000/api/v1/labs/<lab-id>/run

# 3. Check job status
curl http://127.0.0.1:8000/api/v1/jobs/<job-id>

# 4. Get logs
curl http://127.0.0.1:8000/api/v1/jobs/<job-id>/logs

# 5. Download artifacts
curl http://127.0.0.1:8000/api/v1/jobs/<job-id>/artifacts/<artifact-id> -o console.log
```
