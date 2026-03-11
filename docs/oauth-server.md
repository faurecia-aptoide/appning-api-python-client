# Service Account Authentication (Server-to-Server)

This library supports server-to-server authentication using service accounts. For the Android Publisher API, this is the standard approach: your application authenticates with a JWT Bearer token (signed with RS256). No end-user consent is required.

## Obtain API access credentials

To obtain API access credentials, go to the **Developer Portal**:

- **https://developers.appning.com/backoffice/settings/api-access-credentials**

From there you can download a credentials file (e.g. `serviceAccount.json`) with this structure:

```json
{
  "kid": "the-key-id",
  "privateKeyPem": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "clientId": "the-client-id"
}
```

- **`privateKeyPem`** is **private** and must remain local (**never** sent to the server).
- **`kid`** identifies the key used to sign the JWT.
- **`clientId`** identifies the client and must be used as the value for the JWT **`iss`** and **`sub`** claims.

## JWT requirements

### Required claims (`iss` / `sub`)

The JWT **must** include:

- **`iss`**: must be equal to the client’s **`clientId`**
- **`sub`**: must be equal to the client’s **`clientId`**

When you use `JwtBearerCredentials` with `client_id` set from `serviceAccount.json`, the library sets these claims for you.

### Token validity (policy)

The server **only accepts tokens with a maximum validity of 15 minutes**:

- The JWT **must** include `iat` and `exp` (Unix epoch seconds).
- The server validates:
  - `exp` has not expired
  - `iat` is not “in the future” (with clock skew tolerance)
  - **`exp - iat <= 900`** seconds (15 minutes)

A clock skew tolerance of around 60 seconds on the server is recommended. The library generates short-lived tokens when you make requests.

## Overview

1. Obtain service account credentials (`serviceAccount.json`) from the [Developer Portal](https://developers.appning.com/backoffice/settings/api-access-credentials).
2. Load the client with those credentials (JWT Bearer) using `JwtBearerCredentials`.
3. Build the Android Publisher service and call the API.

## Using the credentials

Create JWT Bearer credentials from the service account file and use them with an authorized HTTP client:

```python
import json
import google_auth_httplib2
import httplib2
from googleapiclient.jwt_bearer_credentials import JwtBearerCredentials
from googleapiclient.http import set_user_agent

with open('/path/to/serviceAccount.json', 'r') as f:
    data = json.load(f)

credentials = JwtBearerCredentials(
    kid=data['kid'],
    private_key_pem=data['privateKeyPem'],
    client_id=data.get('clientId')  # required for iss/sub
)

http = set_user_agent(httplib2.Http(timeout=30), 'appning-api-python-client/androidpublisher')
authorized_http = google_auth_httplib2.AuthorizedHttp(credentials, http=http)
```

For Appning/Android Publisher with a custom endpoint, use the JWT Bearer credentials as above (not Application Default Credentials).

## Calling the Android Publisher API

Build the service object and make requests:

```python
from googleapiclient.discovery import build

service = build(
    'androidpublisher',
    'v3',
    http=authorized_http,
    client_options={'api_endpoint': 'https://product.faa.faurecia-aptoide.com/api/8.20240517'}
)

response = service.monetization().onetimeproducts().batchUpdate(
    packageName=package_name,
    body=batch_request_body
).execute()
```

## Complete example

See [samples/androidpublisher/example_custom_endpoint.py](../samples/androidpublisher/example_custom_endpoint.py) for a full working example, including the expected format of `serviceAccount.json` and error handling.

## Responses and troubleshooting

### Response codes

| Code | Meaning | Typical causes |
|------|---------|----------------|
| **200 OK** | Request processed successfully. | — |
| **400 Bad Request** | Invalid payload / validation failure. | Missing required fields, invalid types/formats, business rules not met. |
| **401 Unauthorized** | Authentication failure / invalid token. | Missing or malformed `Authorization` header; malformed JWT; invalid signature; unknown or revoked `kid`; expired token (`exp`); token validity &gt; 15 minutes (`exp - iat > 900`); `iat` too far in the future; missing or wrong `iss`/`sub` (must equal `clientId`). |
| **403 Forbidden** | Token valid but caller lacks permission. | Client (`iss`/`sub`) not authorized for this endpoint; different access level required. |
| **404 Not Found** | Resource not found. | Package not available for monetization, or package does not exist under your credentials. |

### Troubleshooting

- **400** — Validate the request body against the endpoint’s expected schema.
- **401 (invalid signature)** — Confirm `kid` matches the public key registered for your credentials; confirm the private key used to sign matches the server-side public key.
- **401 (invalid issuer/subject)** — Confirm `iss` and `sub` are present and both equal to the `clientId` from `serviceAccount.json`.
- **401 (expired token / TTL)** — Confirm `iat`/`exp` are Unix seconds; confirm `exp - iat <= 900`; ensure system clock is correct (NTP).
- **403** — Confirm the permissions associated with your `clientId` at [developers.appning.com](https://developers.appning.com).
- **404** — Confirm the package name and settings at [developers.appning.com](https://developers.appning.com).
