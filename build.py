import subprocess
import certifi

from version import version

# Customize the name
name = f"StudentApp_v{version}"
certificate_path = certifi.where()

# PyInstaller command
cmd = [
    "pyinstaller",
    "--onefile",
    "--name", "main",
    "--add-data", f"{certificate_path}:certifi",
    "--clean",
    "main.py"
]

# Run command
subprocess.run(cmd)
