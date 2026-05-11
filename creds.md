update dist:
pip3 install build
rm -rf dist
python3 -m build


push to pypi:
pip3 install twine
python3 -m twine upload dist/* -u __token__ -p pypi-AgEIcHlwaS5vcmcCJDJkM2Y4N2Q3LTY4ZjUtNDk3OC04MGM0LWQwNDUxMjk5OTI2YwACKlszLCJkNjg5OWQ4NC0wMDAzLTQ4ZDQtOTY0ZC1kOGEwMjUwNGM3OGIiXQAABiAGkjK8MblnUD7W0ASWtaQqJJTvHhO0TlHgS0KZtDOLbw


# For binary file generation
# 1. Install Rust (installs rustc + cargo)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. Reload shell
source $HOME/.cargo/env

# 3. Install maturin
pip install maturin
