# bash file to push to pypi
#!/bin/bash
set -e

echo "Building..."
rm -rf dist
python3 -m build

echo "Uploading to PyPI..."
# Set PYPI_TOKEN in your environment before running: export PYPI_TOKEN=pypi-...
python3 -m twine upload dist/* --username __token__ -p "${PYPI_TOKEN:?PYPI_TOKEN env var is not set}"

echo "Done!"