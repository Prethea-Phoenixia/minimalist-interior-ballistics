if exist build rmdir build /q /s
if exist dist rmdir dist /q /s
python -m build
pip install .
pause