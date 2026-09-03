# Appning API Client Library for Python

**License:** Apache 2.0

The **Appning API** enables developers to **interact with Appning services** from their own systems (server-to-server). This client library is focused on **Android Publisher** with custom endpoints.

All Appning endpoints are authenticated using **JWT Bearer tokens** signed locally with **RS256**. This library is based on the Google API Python Client and is adapted for use with Appning services.

> This library is an **unofficial fork** of Google’s `google-api-python-client` library and is **maintained independently by Appning**. It is not an official Google product and is provided under the same Apache License 2.0 terms as the upstream project.

## Appning API compatibility

> **Read this before you write code for `oneTimeProducts`.** This client comes
> from Google's Android Publisher discovery document, which Appning does not
> change. Thus the client shows **17 operations** under
> `monetization.onetimeproducts`. Appning has **one** of them. You can call the
> other 16, but they give status 404.

<!-- BEGIN onetimeproducts-compat -->

**Direct methods on `onetimeproducts`**

| Operation | Client call | Status |
|---|---|---|
| `batchUpdate` | `.monetization().onetimeproducts().batchUpdate()` | **Supported** |
| `batchDelete` | `.monetization().onetimeproducts().batchDelete()` | Not implemented — 404 |
| `batchGet` | `.monetization().onetimeproducts().batchGet()` | Not implemented — 404 |
| `delete` | `.monetization().onetimeproducts().delete()` | Not implemented — 404 |
| `get` | `.monetization().onetimeproducts().get()` | Not implemented — 404 |
| `list` | `.monetization().onetimeproducts().list()` | Not implemented — 404 |
| `patch` | `.monetization().onetimeproducts().patch()` | Not implemented — 404 |

**Purchase options** — `.monetization().onetimeproducts().purchaseOptions()`

| Operation | Client call | Status |
|---|---|---|
| `purchaseOptions.batchDelete` | `.purchaseOptions().batchDelete()` | Not implemented — 404 |
| `purchaseOptions.batchUpdateStates` | `.purchaseOptions().batchUpdateStates()` | Not implemented — 404 |

**Offers** — `.monetization().onetimeproducts().purchaseOptions().offers()`

| Operation | Client call | Status |
|---|---|---|
| `purchaseOptions.offers.activate` | `.purchaseOptions().offers().activate()` | Not implemented — 404 |
| `purchaseOptions.offers.batchDelete` | `.purchaseOptions().offers().batchDelete()` | Not implemented — 404 |
| `purchaseOptions.offers.batchGet` | `.purchaseOptions().offers().batchGet()` | Not implemented — 404 |
| `purchaseOptions.offers.batchUpdate` | `.purchaseOptions().offers().batchUpdate()` | Not implemented — 404 |
| `purchaseOptions.offers.batchUpdateStates` | `.purchaseOptions().offers().batchUpdateStates()` | Not implemented — 404 |
| `purchaseOptions.offers.cancel` | `.purchaseOptions().offers().cancel()` | Not implemented — 404 |
| `purchaseOptions.offers.deactivate` | `.purchaseOptions().offers().deactivate()` | Not implemented — 404 |
| `purchaseOptions.offers.list` | `.purchaseOptions().offers().list()` | Not implemented — 404 |

<!-- END onetimeproducts-compat -->

Do not call `purchaseOptions` or `offers` as resources. Appning accepts
`purchaseOptions` only as a **field in the `batchUpdate` request body**.

Appning has plans to add some of these operations. The plans have no release
date. Use only the operations that this table shows as supported.

### Two ways this fails quietly

The two failures are different. Find which one you have first.

**1. `GET`, `PUT` and `DELETE` on the `:batchUpdate` path give status 200 and
change nothing.** The path `.../oneTimeProducts:batchUpdate` accepts four
methods. Only `POST` does work. The other three methods are stubs. Appning keeps
them for compatibility with the legacy service. They do not read or write data.

If you send one of these three requests manually, the server gives status 200.
Nothing changes. This library gives you an empty result, not a result object.
`GET` gives `[]`. `PUT` and `DELETE` give `''`:

```python
# The server gives status 200. No data changed.
response = ...                 # [] from GET, or '' from PUT and DELETE
response["oneTimeProducts"]    # TypeError: string indices must be integers
```

This `TypeError` is usually the first symptom. The message does not show the
cause. To change one-time products, use `POST` only. That is, use
`batchUpdate()`.

**2. `get`, `delete` and `list` give status 404.** These operations use a
different path: `.../oneTimeProducts/{productId}`. Appning has no route for this
path. These operations do not reach the stubs above. They raise `HttpError` with
status 404. The other 13 unsupported operations do the same.

A 404 here shows that Appning does not have this operation. It does not show a
wrong package name. It does not show a permission problem. Look at the table
above first.

### Where this is specified

The authoritative statement lives in the Appning API documentation. **Sign in to
the [Developer Portal](https://developers.appning.com) first** — the API
documentation is not readable anonymously.

Then open
[monetization.onetimeproducts](https://developers.appning.com/api-documentation/docs/appning/android-publisher/monetization.onetimeproducts/monetization.onetimeproducts.md),
or navigate to it: **API Documentation → Appning → Android Publisher →
`monetization.onetimeproducts`**.

If this table and that page ever disagree, the documentation is correct and this
table is stale. Please report it.

> **Note on `list_next()`.** The library makes a `list_next()` pagination helper
> for `list` and for `purchaseOptions.offers.list`. You cannot use either helper,
> because Appning has neither `list` operation.

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
package_name = "com.example.app"

if not os.path.exists(service_account_file):
    raise FileNotFoundError("serviceAccount.json not found. Obtain credentials from the developer portal.")

with open(service_account_file, 'r') as f:
    data = json.load(f)
cred_kwargs = {'kid': data['kid'], 'private_key_pem': data['privateKeyPem']}

if data.get('clientId'):
    cred_kwargs['client_id'] = data['clientId']
credentials = JwtBearerCredentials(**cred_kwargs)

custom_endpoint = 'https://product.faa.faurecia-aptoide.com/api/8.20240517/'
base_http = set_user_agent(httplib2.Http(timeout=30), 'appning-api-python-client/androidpublisher')
authorized_http = google_auth_httplib2.AuthorizedHttp(credentials, http=base_http)

service = build('androidpublisher', 'v3', http=authorized_http, client_options={'api_endpoint': custom_endpoint})

batch_request_body = {
  "requests": [
      {
          "oneTimeProduct": {
              "packageName": package_name,
              "productId": f"coin_pack_etc_{int(time.time())}",
              "listings": [
                  {
                      "languageCode": "pt-BR",
                      "title": "300 Moedas",
                      "description": "Receba 300 moedas instantaneamente"
                  },
                  {
                      "languageCode": "en-US",
                      "title": "300 Coins",
                      "description": "Receive 300 coins instantly"
                  }
              ],
              "purchaseOptions": [
                  {
                      "purchaseOptionId": "default",
                      "buyOption": {
                          "legacyCompatible": True,
                          "multiQuantityEnabled": False
                      },
                      "regionalPricingAndAvailabilityConfigs": [
                          {
                              "regionCode": "US",
                              "price": {
                                  "currencyCode": "USD",
                                  "units": "1",
                                  "nanos": 880000000
                              },
                              "availability": "AVAILABLE"
                          }
                      ]
                  }
              ]
          },
          "updateMask": "listings,purchaseOptions",
          "allowMissing": True,
          "latencyTolerance": "PRODUCT_UPDATE_LATENCY_TOLERANCE_LATENCY_TOLERANT",
          "regionsVersion": {
              "version": "2025/03"
          }
      }
  ]
}

response = service.monetization().onetimeproducts().batchUpdate(
    packageName=package_name, body=batch_request_body
).execute()
```

## Available endpoints

| Service          | Method | Description |
|------------------|--------|-------------|
| Android Publisher | POST   | Batch create/update one-time products (monetization): `androidpublisher/v3/applications/{packageName}/oneTimeProducts:batchUpdate` |

This is the **only** `oneTimeProducts` operation that Appning has. The client
shows 16 more operations, but they give status 404. Read
[Appning API compatibility](#appning-api-compatibility) before you call them.

The base URL for the Appning product API is
`https://product.faa.faurecia-aptoide.com/api/8.20240517`, where the final
segment is the API version your account uses. Set it via
`client_options={'api_endpoint': '...'}` when building the service. The client
appends `androidpublisher/v3/` itself, so a full request URL looks like:

```
https://product.faa.faurecia-aptoide.com/api/8.20240517/androidpublisher/v3/applications/{packageName}/oneTimeProducts:batchUpdate
```

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

The [docs/](docs/) folder contains [Getting Started](docs/start.md), [Installation](docs/install.md), [Service Account Authentication](docs/oauth-server.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Pull requests are welcome.

## Support

For issues with the library, open an issue in the project’s issue tracker with a minimal example and error details. For API-specific questions, refer to the relevant API documentation.
