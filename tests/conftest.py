#!/usr/bin/env python
#
# Copyright © 2026 Appning Lda.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
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
