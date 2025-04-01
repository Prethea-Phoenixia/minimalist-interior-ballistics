rmdir /s /q docs
python -m pdoc -o docs --docformat numpy src/minimalist_interior_ballistics/ --math
pause
