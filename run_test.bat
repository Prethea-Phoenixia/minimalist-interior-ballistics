For /R ballistics %%G In (*.py) Do python -m doctest -v "%%G"
pause