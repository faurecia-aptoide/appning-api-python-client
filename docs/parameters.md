# Standard Parameters

This client uses JWT Bearer authentication for Appning/Android Publisher. API keys (`developerKey`) are not used.

Many API methods support optional parameters. In addition to method-specific parameters, several standard parameters can be applied to requests. These are commonly supported across Google-style discovery APIs.

## Parameters

- **alt** — Specify an alternative response type (e.g. `json`, `media`).
- **fields** — A comma-separated list of fields to include in the response. Nested fields can be specified with parentheses, e.g. `key,parent(child/subsection)`. Use this to limit response size or shape.
- **userIp** — The IP of the end-user making the request. Used for per-user request quotas.
- **quotaUser** — A user ID for the end user, an alternative to `userIp` for applying per-user request quotas.
- **data** — Used for media uploads.
- **mimeType** — Used for media uploads.
- **uploadType** — Used for media uploads (e.g. `multipart`, `resumable`).
- **mediaUpload** — Used for media uploads.

When calling methods via the Python client, pass these as keyword arguments to the method, e.g. `service.resource().list(fields='nextPageToken,items(id)').execute()`. See the [API reference](dyn/index.md) for the specific API you are using.
