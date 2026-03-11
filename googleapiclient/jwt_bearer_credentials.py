# Copyright 2025 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Credentials that generate RS256 JWT Bearer tokens with a kid header.

This module provides JwtBearerCredentials class that generates JWT tokens
signed with RS256 algorithm using a private key. The kid (Key ID) is included
in the JWT header for token validation.
"""

import hashlib
import datetime
import time
from typing import Optional, Dict, Any

try:
    from google.auth import credentials
    from google.auth import crypt
    from google.auth import jwt
    HAS_GOOGLE_AUTH = True
except ImportError:
    HAS_GOOGLE_AUTH = False
    # Define a dummy class if google-auth is not available
    class Credentials:
        pass


if HAS_GOOGLE_AUTH:
    class JwtBearerCredentials(credentials.Credentials):
        """Credentials that generate RS256 JWT Bearer tokens with a kid header.

        This class generates JWT tokens signed with RS256 algorithm using a private key.
        The kid (Key ID) is included in the JWT header for token validation.

        Args:
            kid (str): The Key ID (kid) to include in JWT header.
            private_key_pem (str): The RSA private key in PEM format.
            client_id (str, optional): Client ID from service account (used for iss and sub
                claims when not provided in generate_token). Defaults to 'jwt-bearer' when None.
        """

        def __init__(
            self,
            kid: str,
            private_key_pem: str,
            client_id: Optional[str] = None
        ):
            if not HAS_GOOGLE_AUTH:
                raise EnvironmentError(
                    "JwtBearerCredentials requires google-auth library. "
                    "Please install google-auth."
                )
            
            if not kid:
                raise ValueError("kid is required")
            if not private_key_pem:
                raise ValueError("private_key_pem is required")

            super(JwtBearerCredentials, self).__init__()
            self._kid = kid
            self._private_key_pem = private_key_pem
            self._client_id = client_id
            self._last_token = None  # {'access_token': str, 'expires_at': int} or None
            self._signer = crypt.RSASigner.from_string(private_key_pem)
            self.token = None
            self.expiry = None

        def generate_token(self, claims: Optional[Dict[str, Any]] = None) -> str:
            """Generate a JWT Bearer token with custom claims.

            When iss/sub are not provided in claims, uses client_id (or 'jwt-bearer' if None).
            Does not set aud by default; include it in claims if needed.

            Args:
                claims (dict, optional): JWT claims (iss, sub, exp, iat, etc.).
                    If not provided, minimal claims with iss/sub from client_id are used.

            Returns:
                str: The signed JWT token.
            """
            token_claims = dict(claims) if claims else {}
            iss_sub = self._client_id or 'jwt-bearer'
            if 'iss' not in token_claims:
                token_claims['iss'] = iss_sub
            if 'sub' not in token_claims:
                token_claims['sub'] = iss_sub

            now = int(time.time())
            if 'exp' not in token_claims:
                token_claims['exp'] = now + 3600
            if 'iat' not in token_claims:
                token_claims['iat'] = now

            token = jwt.encode(self._signer, token_claims, key_id=self._kid)
            if isinstance(token, bytes):
                token = token.decode('utf-8')

            self._last_token = {
                'access_token': token,
                'expires_at': token_claims['exp'],
            }
            self.token = token
            self.expiry = datetime.datetime.utcfromtimestamp(token_claims['exp'])

            return token

        def refresh(self, request):
            """Refreshes the access token.

            Generates a token with iss/sub from client_id (or 'jwt-bearer').
            Equivalent to PHP fetchAuthToken().

            Args:
                request: Unused for JWT generation, but required by interface.

            Returns:
                None
            """
            self.generate_token()

        def apply(self, headers, token=None):
            """Apply the token to the headers.

            Args:
                headers (dict): The headers to add the token to.
                token (str, optional): The token to use. If not provided, generates
                    a new token or uses cached token.

            Returns:
                None
            """
            if token is None:
                if not self.valid:
                    self.refresh(None)
                token = self.token

            headers['Authorization'] = 'Bearer {}'.format(token)

        def before_request(self, request, method, url, headers):
            """Performs credential-specific before request logic.

            Args:
                request: Unused, but required by interface.
                method: Unused, but required by interface.
                url: Unused, but required by interface.
                headers (dict): The headers to add the token to.
            """
            self.apply(headers)

        @property
        def kid(self) -> str:
            """The Key ID (kid).

            Returns:
                str: The Key ID.
            """
            return self._kid

        # Alias for backwards compatibility
        def get_kid(self) -> str:
            """Get the Key ID (kid).

            Returns:
                str: The Key ID.
            """
            return self._kid

        def get_cache_key(self) -> str:
            """Gets a cache key for the credentials.

            Returns:
                str: Cache key based on kid.
            """
            return 'jwt_bearer_' + hashlib.md5(self._kid.encode()).hexdigest()

        def get_last_received_token(self) -> Optional[Dict[str, Any]]:
            """Returns the last generated token.

            Returns:
                dict or None: Last token with 'access_token' and 'expires_at' (Unix
                    timestamp), or None if no token has been generated yet.
            """
            return self._last_token

        def get_client_id(self) -> Optional[str]:
            """Get the client ID (used for iss and sub claims when set).

            Returns:
                str or None: The client ID from constructor, or None.
            """
            return self._client_id
else:
    # Fallback class if google-auth is not available
    class JwtBearerCredentials:
        """Placeholder class when google-auth is not installed."""
        
        def __init__(self, *args, **kwargs):
            raise EnvironmentError(
                "JwtBearerCredentials requires google-auth library. "
                "Please install google-auth."
            )
