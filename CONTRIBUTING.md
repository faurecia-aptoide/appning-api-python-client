# Contributing

Contributions are welcome. No contributor license agreement is required.

## How to contribute

1. Fork the repo and clone your fork locally.
2. Create a branch, make your changes, and add or update tests as needed.
3. Run the test suite (see [README.md](README.md#testing)).
4. Keep commit messages clear and descriptive.
5. Open a pull request.

## Development setup

- **Python:** 3.7+
- **Install:** `pip install -e .` and `pip install -r dev-requirements.txt` for tests.
- **Tests:** `pytest tests/` from the project root.
- **Style:** `flake8 googleapiclient/ tests/`; fix with `autopep8 --in-place --recursive googleapiclient/ tests/` if desired.

## Scope

This project focuses on the **Appning API** and **Android Publisher** with JWT Bearer authentication. Keep changes aligned with that scope.
