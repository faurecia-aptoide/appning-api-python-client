# Pytest configuration for appning-api-python-client tests.
#
# Credentials: For Appning, obtain API access credentials from the Developer
# Portal (JWT Bearer, serviceAccount.json). Do not use credentials_file or
# Application Default Credentials for Appning.
#   https://developers.appning.com/backoffice/settings/api-access-credentials

import warnings

# Suppress DeprecationWarning from google.api_core about credentials_file
# (it references cloud.google.com). For Appning we use JWT Bearer credentials
# from the Developer Portal (see link above).
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module="google.api_core.client_options",
)
