
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

**Description**: Allows an employee to upload an invoice image for processing. The image, along with the `user_uuid`, is stored in MongoDB, and processing is triggered.

```shell
curl -X POST "http://localhost:8000/api/v1/invoices/upload" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <auth_token>" \
-d '{
  "img": "<base64_value>",
  "user_uuid": "<user_uuid>"
}'
```

| Element       | Description  | Type   | Required | Notes                            |
|---------------|--------------|--------|----------|----------------------------------|
| Content-Type  | header       | string | required | `application/json`               |
| Authorization | header       | string | required | Bearer `<auth_token>`            |
| img           | body         | string | required | Invoice image in base64 format   |
| user_uuid     | body         | string | optional | UUID of the user uploading the invoice |

**Response on success**:  
```json
{
  "invoice_uuid": "<invoice_uuid>",
  "message": "Upload successful"
}
```

| Element      | Type   | Description            |
|--------------|--------|------------------------|
| invoice_uuid | UUID   | UUID of the invoice     |
| message      | string | Status message          |

### Explanation:
- The `Content-Type` is now `application/json` since the data is sent as a JSON payload.
- The `img` field in the body contains the base64-encoded image.
- The `user_uuid` field in the body identifies the user uploading the invoice.
- The response includes the `invoice_uuid` of the uploaded invoice and a confirmation message.

Here’s the updated Markdown for the DELETE API with `user_uuid` included:

### 2.2 Delete Invoice Image

**Description**: Deletes an invoice image from the database. The request requires the `user_uuid` to log who initiated the deletion.

```shell
curl -X DELETE "http://localhost:8000/api/v1/invoices/<invoice_uuid>?user_uuid=<user_uuid>" \
-H "Authorization: Bearer <auth_token>"
```

| Element       | Description  | Type   | Required | Notes                             |
|---------------|--------------|--------|----------|-----------------------------------|
| Authorization | header       | string | required | Bearer `<auth_token>`             |
| invoice_uuid  | path         | UUID   | required | UUID of the invoice to delete     |
| user_uuid     | query        | string | optional | UUID of the user requesting the deletion |

**Response on success**:  
```json
{
  "message": "Invoice deleted successfully"
}
```

| Element | Type   | Description    |
|---------|--------|----------------|
| message | string | Status message |


### Explanation:
- The `user_uuid` is added as a query parameter in the URL to identify the user requesting the deletion.
- The `invoice_uuid` remains in the path to specify which invoice to delete.
- The response confirms the successful deletion with a status message.


Here's the Markdown for the GET API to retrieve a list of invoices with the specified parameters:

### 2.3 Get Invoice Information

More in `docs/invoice_info.md`

**Description**: Retrieves a list of invoices from the database based on the provided filters and sorting options. The response will include the specified number of invoices per page, along with metadata about each invoice.

```shell
curl -X GET "http://localhost:8000/api/v1/invoices?created_at=<sort_order>&created_by=<user_uuid>&invoice_type=<invoice_type>&page=<page_number>&limit=<limit>&invoice_uuid=<invoice_uuid>" \
-H "Authorization: Bearer <auth_token>"
```

| Element       | Description  | Type   | Required | Notes                                      |
|---------------|--------------|--------|----------|--------------------------------------------|
| Authorization | header       | string | required | Bearer `<auth_token>`                      |
| created_at    | query        | string | optional | Sort by creation date (`asc` or `desc`)    |
| created_by    | query        | string | optional | Filter by `user_uuid` of the invoice creator (if None, take all)|
| invoice_type  | query        | string | optional | Filter by type of invoice (if None, take all)                  |
| invoice_uuid  | query        | string | optional | Id of specific invoice                      |
| page          | query        | number | optional | Page number for pagination (default is 1)   |
| limit         | query        | number | optional | Number of invoices per page (default is 10) |

**Response on success**:  
```json
[
  {
    "invoice_uuid": "string", 
    "invoice_type": "string",  
    "created_at": "ISODate",  
    "created_by": "string",  
    "last_modified_at": "ISODate",  
    "last_modified_by": "string",  
    "status": "string",  
    "invoice_image_base64": "string",  
    "ocr_info": {
      "ori_text": "string",
      "ori_language": "string",
      "text": "string",
      "language": "string"
    },
    "translator": "string",
    "ocr_detector": "string",
    "llm_extractor": "string",
    "post_processor": "string",
    "invoice_info": {
      ...
    }
  },
  {
    "invoice_uuid": "string", 
    ...
  }
]
```

| Element           | Type    | Description                                             |
|-------------------|---------|---------------------------------------------------------|
| invoice_uuid      | UUID    | UUID of the invoice/image                                |
| invoice_type      | string  | Type of the invoice                                      |
| created_at        | ISODate | Timestamp of invoice creation                            |
| created_by        | string  | `user_uuid` of the invoice creator                       |
| last_modified_at  | ISODate | Timestamp of last modification                           |
| last_modified_by  | string  | `user_uuid` of the last modifier                         |
| status            | string  | Status of the invoice (e.g., "not extracted", "completed")|
| invoice_info      | object  | Detail in `docs/invoice_info.md`          |

### Explanation:
- The `created_at` parameter allows sorting the results by creation date in either ascending or descending order.
- The `created_by`, `invoice_type`, `page`, and `limit` parameters filter the results and control pagination.
- The response returns a list of invoice objects, each containing detailed metadata and processing information.

Here's the updated markdown and API for modifying invoice information, incorporating the changes:

### 2.4 Modify Invoice Information

**Description**: Allows an admin or employee to modify the extracted invoice information. The invoice UUID and the new invoice data must be provided. The `user_uuid` parameter helps track who made the update. Only the `invoice_info` field is updated, containing the first 5 keys.

```shell
curl -X PUT "http://localhost:8000/api/v1/invoices/<invoice_uuid>" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <auth_token>" \
-d '{
  "user_uuid": "<user_uuid>",
  "invoice_info": {
    "amount": 1000.00,
    "amount_change": 50.00,
    "amount_shipping": 20.00,
    "currency": "USD",
    "date": "2024-08-29",
    ...
  }
}
```

| Element       | Description                | Type   | Required | Notes                       |
|---------------|----------------------------|--------|----------|-----------------------------|
| Content-Type  | Request header             | string | required | application/json            |
| Authorization | Request header             | string | required | Bearer JWT token            |
| user_uuid     | Request body               | UUID   | optional | UUID of the user updating the invoice |
| invoice_info  | Request body               | JSON   | required | Updated invoice_info as in `docs/invoice_info.md` |

**Response body on success**:

```json
{
  "invoice_uuid": "<invoice_uuid>",
  "message": "Invoice information updated."
}
```

| Element      | Type   | Description                    |
|--------------|--------|--------------------------------|
| invoice_uuid | UUID   | UUID of the updated invoice     |
| message       | string | Message of the update process   |



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
  ...
}
```

| Element        | Type   | Description                  |
|----------------|--------|------------------------------|
| total_invoices | int    | Total number of invoices     |

