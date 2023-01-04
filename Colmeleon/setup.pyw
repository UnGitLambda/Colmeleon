# -*- coding: utf-8 -*-
"""
Created on Sun May  8 20:57:23 2022

@author: Eyal Cohen
"""

import sys
import os
if __name__ == "__main__":
    import ctypes
    
    def Mbox(title, text, style):
        return ctypes.windll.user32.MessageBoxW(0, text, title, style)
    
    if sys.version_info < (3,7):
        print("This program runs under python 3.7 or more. To use it please "+
              "get you version of python up to date.")
        Mbox("Errors", "This program runs under python 3 or more. To use it"+
             " please get you version of python up to date.")

import subprocess
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict

def should_install_requirement(requirement):
    should_install = False
    try:
        pkg_resources.require(requirement)
    except (DistributionNotFound, VersionConflict):
        should_install = True
    return should_install


def install_packages(requirement_list):
    try:
        requirements = [
            requirement
            for requirement in requirement_list
            if should_install_requirement(requirement)
        ]
        if len(requirements) > 0:
            if not os.path.exists("./Colmeleon_library"):
                os.mkdir("./Colmeleon_library")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install",
                                   "-t", "./Colmeleon_library",
                                   *requirements])
                sys.path.insert(0, os.path.abspath("./Colmeleon_library"))
            except:
                subprocess.check_call([sys.executable, "-m", "pip", "install",
                                   *requirements])
        else:
            print("Requirements already satisfied.")

    except Exception as e:
        print(e)
try:
    to_install = ["tkinterdnd2", "opencv-python", "matplotlib",
                  "datetime", "argparse", "pathlib", "numpy", "deprecated"]
    install_packages(to_install)
except:
    pass
try:
    if os.path.exists("./Colmeleon_library"):
        for elem in os.listdir("./Colmeleon_library"):
            sys.path.insert(0, os.path.abspath(elem))
    elif os.path.exists("../Colmeleon/Colmeleon_library"):
        for elem in os.listdir("../Colmeleon_library"):
            sys.path.insert(0, os.path.abspath(elem))
except:
    pass