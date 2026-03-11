# Samples

Samples in this repository are for **Android Publisher** only (Appning API with JWT Bearer authentication).

## Android Publisher

| Sample | Description |
|--------|-------------|
| [androidpublisher/](androidpublisher/) | JWT Bearer authentication and batch update of one-time products (monetization). |

### Running the sample

1. Obtain credentials from the [Developer Portal](https://developers.appning.com/backoffice/settings/api-access-credentials) and save as `serviceAccount.json` in the project root (or adjust the path in the sample).
2. From the project root:
   ```sh
   cd samples/androidpublisher
   python example_custom_endpoint.py
   ```

The sample calls the Android Publisher batch update endpoint (one-time products). It uses a custom API endpoint and JWT Bearer tokens; see the [main README](../README.md) for authentication details.
