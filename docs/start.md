# Getting Started

This document provides the basic information you need to start using the library with the Android Publisher API. It covers important library concepts and gives links to more information.

## Setup

1. Obtain credentials from the **Developer Portal**: [developers.appning.com/backoffice/settings/api-access-credentials](https://developers.appning.com/backoffice/settings/api-access-credentials). Download a credentials file (e.g. `serviceAccount.json`) with `kid`, `privateKeyPem`, and `clientId`.
2. [Install](install.md) the library.

## Authentication

This library uses **JWT Bearer** authentication (RS256) for Appning/Android Publisher. Use a service account JSON file (e.g. `serviceAccount.json`) containing `kid`, `privateKeyPem`, and `clientId`. The server requires `iss` and `sub` to equal `clientId`, and accepts tokens with a maximum validity of 15 minutes. See the [main README](../README.md#authentication-jwt-bearer) and [Service Account Authentication](oauth-server.md) for the full format and JWT requirements.

## Building and calling a service

### Build the authorized HTTP client

Create credentials from the service account file and wrap an HTTP client so that requests are signed with a JWT Bearer token.

```python
import json
import google_auth_httplib2
import httplib2
from googleapiclient.http import set_user_agent
from googleapiclient.jwt_bearer_credentials import JwtBearerCredentials

with open('serviceAccount.json', 'r') as f:
    data = json.load(f)
credentials = JwtBearerCredentials(
    kid=data['kid'],
    private_key_pem=data['privateKeyPem'],
    client_id=data.get('clientId')
)
http = set_user_agent(httplib2.Http(timeout=30), 'appning-api-python-client/androidpublisher')
authorized_http = google_auth_httplib2.AuthorizedHttp(credentials, http=http)
```

### Build the service object

Use the [build()](https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.discovery-module.html#build) function with the authorized HTTP client. For a custom endpoint (Appning), pass `client_options={'api_endpoint': 'https://...'}`.

```python
from googleapiclient.discovery import build

# Custom endpoint (Appning)
service = build(
    'androidpublisher',
    'v3',
    http=authorized_http,
    client_options={'api_endpoint': 'https://product.faa.faurecia-aptoide.com/api/8.20200601/'}
)

# Or default Google endpoint
# service = build('androidpublisher', 'v3', http=authorized_http)
```

### Calling the API

Access resources and methods from the service object in the form `service.resource().method(args).execute()`. For example, to call the batch update for one-time products:

```python
from googleapiclient.errors import HttpError

package_name = 'com.example.app'
batch_request_body = {'requests': [...]}  # See sample for full structure

try:
    response = service.monetization().onetimeproducts().batchUpdate(
        packageName=package_name,
        body=batch_request_body
    ).execute()
except HttpError as e:
    print('Error:', e.resp.status, e.error_details)
```

### Handling the result

The response is a dictionary (or object) built from the JSON response. Use the API’s reference for response fields. You can inspect it with:

```python
import json
print(json.dumps(response, indent=2))
```

Missing or optional fields may be absent; use the `fields` parameter in requests when you need specific response fields. See the [example](../samples/androidpublisher/example_custom_endpoint.py) for a full flow including error handling.
