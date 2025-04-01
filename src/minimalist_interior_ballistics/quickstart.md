# Minimalist Interior Ballistics
is a Python library for lumped parameters, zero dimension interior ballistics calculation, written by [Jinpeng Zhai](mailto:914962409@qq.com). 


## Quickstart

## Author's Note
This package is a developed out of, and with much of the lessons learned from [Phoenix's Interior Ballistic Solver (PIBS)](https://github.com/Prethea-Phoenixia/Phoenix-s-Interior-Ballistic-Solver-PIBS), which was written during my undergraduate years. 

Development of PIBS is discontinued, due to fundamental issues with the underlying architecture choices, specifically:
* lack of coherent datastrcutures leading to massive code duplication between gun types and between forward and backwards solving, which makes further development difficult.
* the (ab)use of error handling to signal certain operational conditions resulting in complex and hard to diagnose failure states.
* the choice of tkinter as the underlying GUI library greatly complicated programming for, and maintaining the user facing code of PIBS. 

Minimalist Interior Ballistics attempts to boil PIBS down to the basics and condensing out the good bits, with a more conventional Python library packaging structure.