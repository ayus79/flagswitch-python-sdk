#!/bin/bash
set -e

echo "Building..."
rm -rf dist
python3 -m build

echo "Uploading to PyPI..."
python3 -m twine upload dist/* --username __token__ --password "pypi-AgEIcHlwaS5vcmcCJDJkM2Y4N2Q3LTY4ZjUtNDk3OC04MGM0LWQwNDUxMjk5OTI2YwACKlszLCJkNjg5OWQ4NC0wMDAzLTQ4ZDQtOTY0ZC1kOGEwMjUwNGM3OGIiXQAABiAGkjK8MblnUD7W0ASWtaQqJJTvHhO0TlHgS0KZtDOLbw"

echo "Done!"
