@echo off
if exist "../options/tosetup.txt" (
	start "python3" "../Colmeleon/setup.pyw"&del "../options/tosetup.txt"
)
start "python3" "../Colmeleon/GUI.pyw"
