python -m pip install --upgrade build
python -m pip install --upgrade twine
pause
python -m build
pause
python -m twine upload --repository testpypi --config-file .pypirc --skip-existing dist/* --verbose
pause