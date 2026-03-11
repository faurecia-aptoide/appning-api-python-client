# Appning API Client Library for Python

**License:** Apache 2.0

The **Appning API** enables developers to **interact with Appning services** from their own systems (server-to-server). This client library is focused on **Android Publisher** with custom endpoints.

All Appning endpoints are authenticated using **JWT Bearer tokens** signed locally with **RS256**. This library is based on the Google API Python Client and is adapted for use with Appning services.

> This library is an **unofficial fork** of Google’s `google-api-python-client` library and is **maintained independently by Appning**. It is not an official Google product and is provided under the same Apache License 2.0 terms as the upstream project.

## Requirements

- [Python 3.7 or higher](https://www.python.org/)

## Installation

### pip

The preferred method is via [pip](https://pip.pypa.io/). From the project root:

```sh
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e .
```

Or install the published package:

```sh
pip install appning-api-python-client
```

This library relies on `google-auth` and `google-auth-httplib2` for authentication and HTTP transport. They are installed automatically as dependencies.

## Authentication (JWT Bearer)

### Obtain API access credentials

Obtain API access credentials from the **Developer Portal**:

- **https://developers.appning.com/backoffice/settings/api-access-credentials**

From there you can download a credentials file (e.g. `serviceAccount.json`) with this structure:

```json
{
    "kid": "the-key-id",
    "privateKeyPem": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    "clientId": "the-client-id"
}
```

- **`privateKeyPem`** is **private** and must remain local (never sent to the server).
- **`kid`** identifies the key used to sign the JWT.
- **`clientId`** identifies the client and must be used as the JWT **`iss`** and **`sub`** claims.

### JWT requirements

- **Required claims:** The JWT must include `iss` and `sub`, both set to the client’s **`clientId`**.
- **Token validity:** The server only accepts tokens with a **maximum validity of 15 minutes** (`exp - iat <= 900` seconds). The JWT must include `iat` and `exp` (Unix epoch seconds). The library handles this when you use `JwtBearerCredentials` with the credentials file.

For full details (clock skew, error responses), see [Service Account Authentication](docs/oauth-server.md).

### Basic Usage Example

See [`samples/androidpublisher/example_custom_endpoint.py`](samples/androidpublisher/example_custom_endpoint.py) for a complete example.

```python
import json
import os
import time
import google_auth_httplib2
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import set_user_agent
from googleapiclient.jwt_bearer_credentials import JwtBearerCredentials

service_account_file = 'serviceAccount.json'
if not os.path.exists(service_account_file):
    raise FileNotFoundError("serviceAccount.json not found. Obtain credentials from the developer portal.")

with open(service_account_file, 'r') as f:
    data = json.load(f)
cred_kwargs = {'kid': data['kid'], 'private_key_pem': data['privateKeyPem']}
if data.get('clientId'):
    cred_kwargs['client_id'] = data['clientId']
credentials = JwtBearerCredentials(**cred_kwargs)

custom_endpoint = 'https://product.faa.faurecia-aptoide.com/api/8.20200601/'
base_http = set_user_agent(httplib2.Http(timeout=30), 'appning-api-python-client/androidpublisher')
authorized_http = google_auth_httplib2.AuthorizedHttp(credentials, http=base_http)

service = build('androidpublisher', 'v3', http=authorized_http, client_options={'api_endpoint': custom_endpoint})
package_name = "com.example.app"
batch_request_body = {"requests": [{...}]}  # See sample for full body

response = service.monetization().onetimeproducts().batchUpdate(
    packageName=package_name, body=batch_request_body
).execute()
```

## Available endpoints

| Service          | Method | Description |
|------------------|--------|-------------|
| Android Publisher | POST   | Batch create/update one-time products (monetization): `applications/{packageName}/oneTimeProducts:batchUpdate` |

The base URL for the Appning product API is typically `https://product.faa.faurecia-aptoide.com/api/8.20240517` (or the version your account uses). Set it via `client_options={'api_endpoint': '...'}` when building the service.

## Examples

- **Android Publisher batch update:** [samples/androidpublisher/example_custom_endpoint.py](samples/androidpublisher/example_custom_endpoint.py) — JWT Bearer auth and batch updates of one-time products (monetization).

## Testing

### How to run tests

1. **Use a virtual environment** (recommended):

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. **Install the package in editable mode and test dependencies:**

   The test suite requires several dependencies (e.g. `pytest`, `parameterized`, `mox`, `webtest`). Install them all with:

   ```sh
   pip install -e .
   pip install -r dev-requirements.txt
   ```

   Without `dev-requirements.txt`, collection may fail with `ModuleNotFoundError` (e.g. `No module named 'parameterized'`).

3. **Run the test suite:**

   From the project root:

   ```sh
   pytest tests/
   ```

   Or with Python module (if `pytest` is not on your PATH):

   ```sh
   python -m pytest tests/
   ```

   Optional: run with coverage:

   ```sh
   pytest tests/ --cov=googleapiclient --cov-report=term-missing
   ```

4. **Run the Android Publisher sample (manual/integration):**

   Requires a valid `serviceAccount.json` in the project root (or path used by the sample). This calls a real or custom endpoint:

   ```sh
   cd samples/androidpublisher
   python example_custom_endpoint.py
   ```

### What is tested

- **Unit tests** (`tests/`) — Core client library (discovery, HTTP, auth, mocks). No live API calls.
- **Android Publisher sample** — Manual verification against a real or custom endpoint; not run in CI unless configured with credentials.

Credential-related deprecation warnings from dependencies (e.g. `credentials_file`) are suppressed in tests. For Appning, **obtain credentials from the [Developer Portal](https://developers.appning.com/backoffice/settings/api-access-credentials)** (JWT Bearer / `serviceAccount.json`), not via Application Default Credentials or `credentials_file`.

### Code style

```sh
flake8 googleapiclient/ tests/
autopep8 --in-place --recursive googleapiclient/ tests/
```

## API responses and troubleshooting

- **200 OK** — Request processed successfully.
- **400 Bad Request** — Invalid payload or validation failure (missing required fields, invalid types).
- **401 Unauthorized** — Authentication failure: missing or malformed `Authorization` header, malformed JWT, invalid signature, unknown/revoked `kid`, expired token, or token validity &gt; 15 minutes. Ensure `iss` and `sub` equal your `clientId`.
- **403 Forbidden** — Token valid but caller lacks permission for this operation; check permissions for your `clientId` at [developers.appning.com](https://developers.appning.com).
- **404 Not Found** — Resource not found (e.g. package not available for monetization or not under your account).

See [Service Account Authentication](docs/oauth-server.md#responses-and-troubleshooting) for more detail.

## Documentation

The [docs/](docs/) folder contains [Getting Started](docs/start.md), [Installation](docs/install.md), [Service Account Authentication](docs/oauth-server.md), and the [Android Publisher alignment plan](docs/ANDROID_PUBLISHER_ALIGNMENT_PLAN.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Pull requests are welcome.

## Support

For issues with the library, open an issue in the project’s issue tracker with a minimal example and error details. For API-specific questions, refer to the relevant API documentation.
