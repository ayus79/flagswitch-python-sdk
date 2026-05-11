#!/bin/bash
set -e

source "$HOME/.cargo/env"

echo "Building..."
maturin build --release --interpreter python3.11 python3.12 python3.13

echo "Uploading to PyPI..."
python3 -m twine upload target/wheels/*.whl --username __token__ --password "$PYPI_TOKEN"

echo "Done!"
