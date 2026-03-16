#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2026 Appning Lda. All Rights Reserved.
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

"""Example: AndroidPublisher with Custom Endpoint and JWT Bearer Authentication.

This example demonstrates:
1. Using JWT Bearer credentials for authentication
2. Customizing the API endpoint (rootUrl)
3. Making batch update requests to AndroidPublisher API

Usage:
  $ python example_custom_endpoint.py
"""

__author__ = "nuno.gomes@forvia.com"

import json
import os
import sys
import time

import google_auth_httplib2
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import set_user_agent
from googleapiclient.jwt_bearer_credentials import JwtBearerCredentials


def main():
    """Main function demonstrating custom endpoint usage."""
    
    # ============================================================
    # 1. Load credentials from serviceAccount.json
    # ============================================================
    service_account_file = os.path.join(
        os.path.dirname(__file__), '..', '..', 'serviceAccount.json'
    )
    
    if not os.path.exists(service_account_file):
        print("Error: serviceAccount.json not found.")
        print("Please create a serviceAccount.json file in the project root with:")
        print('  {')
        print('    "kid": "your-key-id",')
        print('    "privateKeyPem": "-----BEGIN RSA PRIVATE KEY-----\\n..."')
        print('  }')
        sys.exit(1)

    try:
        with open(service_account_file, 'r') as f:
            service_account_data = json.load(f)

        kid = service_account_data.get('kid')
        private_key_pem = service_account_data.get('privateKeyPem')
        client_id = service_account_data.get('clientId')

        if not kid or not private_key_pem:
            print("Error: serviceAccount.json must contain 'kid' and 'privateKeyPem'.")
            sys.exit(1)

        print("✅ Credentials loaded successfully")

    except json.JSONDecodeError:
        print("Error: serviceAccount.json is not valid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading credentials: {str(e)}")
        sys.exit(1)

    # ============================================================
    # 2. Create JWT Bearer credentials
    # ============================================================
    # If clientId is present in serviceAccount.json, it is used for iss and sub claims
    try:
        cred_kwargs = {'kid': kid, 'private_key_pem': private_key_pem, 'client_id':client_id}
        credentials = JwtBearerCredentials(**cred_kwargs)
        print("✅ JWT Bearer credentials created")
    except Exception as e:
        print(f"Error creating credentials: {str(e)}")
        sys.exit(1)

    # ============================================================
    # 3. Define custom endpoint (equivalent to PHP's rootUrl)
    # ============================================================
    # Change this to your custom endpoint
    custom_endpoint = 'http://product.faa.local.faurecia-aptoide.com/api/8.20240517'

    # For standard Google API, use:
    # custom_endpoint = None  # Will use default Google endpoint

    print(f"\n📡 Using endpoint: {custom_endpoint if custom_endpoint else 'Default Google API endpoint'}")

    # ============================================================
    # 4. Build service with custom endpoint
    # ============================================================
    # Build an http client with a proper User-Agent header.
    # The default library User-Agent is "(gzip)" which some custom
    # servers reject. We set a clean User-Agent before building.
    try:
        base_http = httplib2.Http(timeout=30)
        base_http = set_user_agent(base_http, 'appning-api-python-client/androidpublisher')
        authorized_http = google_auth_httplib2.AuthorizedHttp(credentials, http=base_http)

        if custom_endpoint:
            # Build with custom endpoint and custom http
            service = build(
                'androidpublisher',
                'v3',
                http=authorized_http,
                client_options={'api_endpoint': custom_endpoint}
            )
        else:
            # Build with default endpoint and custom http
            service = build(
                'androidpublisher',
                'v3',
                http=authorized_http,
            )

        print(f"✅ Service created successfully")
        print(f"   Base URL: {service._baseUrl}")

    except Exception as e:
        print(f"Error building service: {str(e)}")
        sys.exit(1)

    # ============================================================
    # 5. Prepare batch update request
    # ============================================================
    package_name = "com.example.app"

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
    
    # ============================================================
    # 6. Make API call
    # ============================================================
    print(f"\n🚀 Calling batchUpdate for package: {package_name}")
    print("   This is a demonstration - modify package_name to use a real package")
    
    try:
        response = service.monetization().onetimeproducts().batchUpdate(
            packageName=package_name,
            body=batch_request_body
        ).execute()
        
        print("\n✅ Success!")
        print(json.dumps(response, indent=2))
        
    except HttpError as e:
        print(f"\n❌ HTTP Error (HTTP {e.resp.status}): {e.error_details}")
        if e.content:
            try:
                error_content = json.loads(e.content.decode('utf-8'))
                print("Error details:")
                print(json.dumps(error_content, indent=2))
            except (json.JSONDecodeError, AttributeError):
                print(f"Error content: {e.content}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
