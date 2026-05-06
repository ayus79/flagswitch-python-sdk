regenerate dist:
cd /Users/ayushcontractor/Desktop/flagswitch-sdk && python3 -m build

push to pypi:
pip3 install twine
python3 -m twine upload dist/* -u __token__ -p pypi-AgEIcHlwaS5vcmcCJDJkM2Y4N2Q3LTY4ZjUtNDk3OC04MGM0LWQwNDUxMjk5OTI2YwACKlszLCJkNjg5OWQ4NC0wMDAzLTQ4ZDQtOTY0ZC1kOGEwMjUwNGM3OGIiXQAABiAGkjK8MblnUD7W0ASWtaQqJJTvHhO0TlHgS0KZtDOLbw
