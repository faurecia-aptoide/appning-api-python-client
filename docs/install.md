# Installation

This page contains information about installing the Appning API Client Library for Python.

## Requirements

* [Python 3.7 or higher](https://www.python.org/)

## Obtaining the client library

### pip (recommended)

The preferred method is via [pip](https://pip.pypa.io/). From your project root, use a virtual environment (recommended):

```sh
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e .
```

To install the published package instead of from source:

```sh
pip install google-api-python-client
```

### Dependencies

This library depends on `google-auth` and `google-auth-httplib2` for authentication and HTTP transport. They are installed automatically when you install the client. The client uses discovery documents cached in the library to build API services (e.g. Android Publisher v3).

For more details, examples, and authentication (JWT Bearer / Appning), see the [main README](../README.md).
