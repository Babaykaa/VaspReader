import subprocess


print(subprocess.check_output(f'py -m ensurepip --upgrade', shell=True, universal_newlines=True))
dependencies = 'freetype-py, matplotlib, matplotlib-inline, numpy, pandas, paramiko, Pillow, psgtray, pygame, PyOpenGL, PyOpenGL-accelerate, pypiwin32, PySimpleGUI, PySimpleGUIQt, pywin32, pywin32-ctypes, simplejson, XlsxWriter'
dependencies = dependencies.split(', ')
for dependence in dependencies:
    print(subprocess.check_output(f'pip install {dependence}', shell=True, universal_newlines=True))
