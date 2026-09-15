"""Build a standalone executable with PyInstaller.

Windows:  python build_windows.py
macOS:    python3 build_windows.py   (produces a .app / unix binary)

Requires: pip install pyinstaller
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SEP = ";" if os.name == "nt" else ":"  # PyInstaller --add-data separator


def main():
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "Cornelia",
        "--add-data", f"{os.path.join(ROOT, 'assets')}{SEP}assets",
        "--add-data", f"{os.path.join(ROOT, 'data')}{SEP}data",
        os.path.join(ROOT, "main.py"),
    ]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
