
# API Documentation

## Table of Contents
1. [User Authentication](#user-authentication)
    - [1.1 Login](#11-login)
    - [1.2 Register](#12-register)
    - [1.3 Logout](#13-logout)
2. [Invoice Management](#invoice-management)
    - [2.1 Upload Invoice Image](#21-upload-invoice-image)
    - [2.2 Delete Invoice Image](#22-delete-invoice-image)
    - [2.3 Get Invoice Information](#23-get-invoice-information)
    - [2.4 Modify Invoice Information](#24-modify-invoice-information)
3. [Admin Dashboard](#admin-dashboard)
    - [3.1 Get System Metrics](#31-get-system-metrics)
    - [3.2 Get All Invoices](#32-get-all-invoices)

---

## 1. User Authentication

### 1.1 Login

**Description**: Authenticates the user and returns a token for session management.

```shell
curl -X POST "http://localhost:8000/api/v1/auth/login" \
-H "Content-Type: application/json" \
-d '{"username": "<username>", "password": "<password>"}'
```

| Element      | Description  | Type   | Required | Notes                            |
|--------------|--------------|--------|----------|----------------------------------|
| Content-Type | header       | string | required | application/json                 |
| username     | body         | string | required | User’s username                  |
| password     | body         | string | required | User’s password                  |

**Response on success**:  
```json
{
  "token": "<auth_token>",
  "user_id": "<user_id>"
}
```

| Element | Type   | Description         |
|---------|--------|---------------------|
| token   | string | Authentication token |
| user_id | string | User's unique ID     |


### 1.2 Register

**Description**: Registers a new user to the system.

```shell
curl -X POST "http://localhost:8000/api/v1/auth/register" \
-H "Content-Type: application/json" \
-d '{"username": "<username>", "password": "<password>", "email": "<email>"}'
```

| Element      | Description  | Type   | Required | Notes               |
|--------------|--------------|--------|----------|---------------------|
| Content-Type | header       | string | required | application/json    |
| username     | body         | string | required | Desired username    |
| password     | body         | string | required | Desired password    |
| email        | body         | string | required | User's email address |

**Response on success**:  
```json
{
  "user_id": "<user_id>",
  "message": "Registration successful"
}
```

| Element  | Type   | Description         |
|----------|--------|---------------------|
| user_id  | string | User's unique ID     |
| message  | string | Status message       |


### 1.3 Logout

**Description**: Logs out the user and invalidates the session token.

```shell
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
-H "Authorization: Bearer <auth_token>"
```

| Element      | Description  | Type   | Required | Notes             |
|--------------|--------------|--------|----------|-------------------|
| Authorization| header       | string | required | Bearer <auth_token> |

**Response on success**:  
```json
{
  "message": "Logout successful"
}
```

| Element | Type   | Description    |
|---------|--------|----------------|
| message | string | Status message |


## 2. Invoice Management

### 2.1 Upload Invoice Image

**Description**: Allows an employee to upload an invoice image for processing. The image is stored in MongoDB, and processing is triggered.

```shell
curl -X POST "http://localhost:8000/api/v1/invoices/upload" \
-H "Content-Type: multipart/form-data" \
-H "Authorization: Bearer <auth_token>" \
-F file=@<local_file> 
```

| Element       | Description  | Type   | Required | Notes                         |
|---------------|--------------|--------|----------|-------------------------------|
| Content-Type  | header       | string | required | multipart/form-data            |
| Authorization | header       | string | required | Bearer <auth_token>           |
| file          | body         | image  | required | Invoice image in base64 format |

**Response on success**:  
```json
{
  "invoice_id": "<invoice_id>",
  "message": "Upload successful"
}
```

| Element    | Type   | Description        |
|------------|--------|--------------------|
| invoice_id | UUID   | UUID of the invoice|
| message    | string | Status message     |


### 2.2 Delete Invoice Image

**Description**: Deletes an invoice image from the database.

```shell
curl -X DELETE "http://localhost:8000/api/v1/invoices/<invoice_id>" \
-H "Authorization: Bearer <auth_token>"
```

| Element       | Description  | Type   | Required | Notes                        |
|---------------|--------------|--------|----------|------------------------------|
| Authorization | header       | string | required | Bearer <auth_token>          |
| invoice_id    | path         | UUID   | required | UUID of the invoice to delete |

**Response on success**:  
```json
{
  "message": "Invoice deleted successfully"
}
```

| Element | Type   | Description    |
|---------|--------|----------------|
| message | string | Status message |


### 2.3 Get Invoice Information

**Description**: Retrieves processed information for a specific invoice.

```shell
curl -X GET "http://localhost:8000/api/v1/invoices/<invoice_id>" \
-H "Authorization: Bearer <auth_token>"
```

| Element       | Description  | Type   | Required | Notes                        |
|---------------|--------------|--------|----------|------------------------------|
| Authorization | header       | string | required | Bearer <auth_token>          |
| invoice_id    | path         | UUID   | required | UUID of the invoice          |

**Response on success**:  
```json
{
  "invoice_id": "<invoice_id>",
  "invoice_data": {
    "date": "2024-08-29",
    "amount": "500.00",
    "vendor": "Company Inc.",
    "items": [...]
  }
}
```

| Element     | Type   | Description           |
|-------------|--------|-----------------------|
| invoice_id  | UUID   | UUID of the invoice   |
| invoice_data| object | Processed invoice data|

### 2.4 Modify Invoice Information
This API allows an admin or employee to modify the extracted invoice information. The image UUID and the new invoice data must be provided.

```json
curl -X PUT "http://localhost:8000/api/v1/invoices/<invoice_id>/modify" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <auth_token>" \
-d '{
  "uuid": "<image_uuid>",
  "invoice_data": {
    "total_amount": "1000.00",
    "date": "2024-08-29",
    "vendor": "ABC Corp",
    "items": [
      {
        "description": "Item 1",
        "amount": "500.00"
      },
      {
        "description": "Item 2",
        "amount": "500.00"
      }
    ]
  }
}
```

| Element       | Description                | Type   | Required | Notes                        |
|---------------|----------------------------|--------|----------|------------------------------|
| Content-Type  | Request header             | string | required | application/json             |
| Authorization | Request header             | string | required | Bearer JWT token             |
| uuid          | Request body               | UUID   | required | UUID of the invoice image    |
| invoice_data  | Request body               | JSON   | required | Updated invoice information   |



**Response body on success**:

```json
{
  "uuid": "image_uuid",
  "status": "Invoice information updated."
}
```

| Element | Type   | Description                     |
|---------|--------|---------------------------------|
| uuid    | UUID   | UUID of the updated image       |
| status  | string | Status of the update process    |

## 3. Admin Dashboard

### 3.1 Get System Metrics

**Description**: Retrieves metrics about the system such as the number of invoices processed, active users, and system performance.

```shell
curl -X GET "http://localhost:8000/api/v1/admin/metrics" \
-H "Authorization: Bearer <admin_auth_token>"
```

| Element       | Description  | Type   | Required | Notes                        |
|---------------|--------------|--------|----------|------------------------------|
| Authorization | header       | string | required | Bearer <admin_auth_token>     |

**Response on success**:  
```json
{
  "total_invoices": 1000,
  "active_users": 50,
  "system_uptime": "99.99%"
}
```

| Element        | Type   | Description                  |
|----------------|--------|------------------------------|
| total_invoices | int    | Total number of invoices     |
| active_users   | int    | Number of active users       |
| system_uptime  | string | System uptime percentage     |


### 3.2 Get All Invoices

**Description**: Retrieves a list of all invoices processed in the system.

```shell
curl -X GET "http://localhost:8000/api/v1/admin/invoices" \
-H "Authorization: Bearer <admin_auth_token>"
```

| Element       | Description  | Type   | Required | Notes                        |
|---------------|--------------|--------|----------|------------------------------|
| Authorization | header       | string | required | Bearer <admin_auth_token>     |

**Response on success**:  
```json
{
  "invoices": [
    {
      "invoice_id": "<invoice_id>",
      "date": "2024-08-29",
      "amount": "500.00",
      "vendor": "Company Inc."
    },
    ...
  ]
}
```

| Element  | Type   | Description             |
|----------|--------|-------------------------|
| invoices | array  | List of processed invoices|

---

This documentation provides a clear overview of each API endpoint, its purpose, and the expected inputs and outputs, ensuring smooth development and integration processes.