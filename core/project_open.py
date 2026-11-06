# core/project_open.py
import os
import shutil
import subprocess
from config import VSCODE_EXE, ANDROID_STUDIO_EXE


def open_in_explorer(folder: str):
    os.startfile(folder)


def open_in_vscode(folder: str):
    try:
        subprocess.Popen([VSCODE_EXE, folder], shell=True)
    except FileNotFoundError:
        os.startfile(folder)


def open_in_android_studio(folder: str):
    if not os.path.isfile(ANDROID_STUDIO_EXE):
        os.startfile(folder)
        return
    subprocess.Popen([ANDROID_STUDIO_EXE, folder])


def vscode_available() -> bool:
    return shutil.which(VSCODE_EXE) is not None


def android_studio_available() -> bool:
    return os.path.isfile(ANDROID_STUDIO_EXE)