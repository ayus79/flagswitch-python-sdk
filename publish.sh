#!/bin/bash
set -e

echo "Building..."
rm -rf dist
python3 -m build

echo "Uploading to PyPI..."
python3 -m twine upload dist/* --username __token__ --password "$PYPI_TOKEN"

echo "Done!"
