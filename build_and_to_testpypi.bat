python -m build
pause
python -m twine upload --repository testpypi --config-file .pypirc --skip-existing dist/* 
pause