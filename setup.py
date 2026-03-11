# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Setup script for Appning API Python client.

Appning API Client Library for Python. Focused on Android Publisher with
JWT Bearer authentication and custom endpoints. Built on the Google API
Python client.
"""
from __future__ import print_function

import io
import os
import sys

from setuptools import setup

if sys.version_info < (3, 7):
    print(
        "appning-api-python-client requires Python >= 3.7.",
        file=sys.stderr,
    )
    sys.exit(1)

packages = ["apiclient", "googleapiclient", "googleapiclient/discovery_cache"]

install_requires = [
    "httplib2>=0.19.0,<1.0.0",
    "google-auth>=1.32.0,<3.0.0,!=2.24.0,!=2.25.0",
    "google-auth-httplib2>=0.2.0,<1.0.0",
    "google-api-core>=1.31.5,<3.0.0,!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0",
    "uritemplate>=3.0.1,<5",
]

package_root = os.path.abspath(os.path.dirname(__file__))

readme_path = os.path.join(package_root, "README.md")
with io.open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

version = {}
with open(os.path.join(package_root, "googleapiclient", "version.py")) as f:
    exec(f.read(), version)
version_str = version["__version__"]

setup(
    name="appning-api-python-client",
    version=version_str,
    description="Appning API Client Library for Python (Android Publisher, JWT Bearer)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Appning",
    author_email="nuno.gomes@forvia.com",
    url="https://developers.appning.com",
    project_urls={
        "Documentation": "https://docs.appning.com/api-documentation",
    },
    install_requires=install_requires,
    python_requires=">=3.7",
    packages=packages,
    package_data={"googleapiclient": ["discovery_cache/documents/*.json"]},
    license="Apache 2.0",
    keywords="appning android publisher jwt bearer api client",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
