import PyInstaller.__main__

PyInstaller.__main__.run([
    "src/main.py",
    "--paths=src",
    "--onefile",
    "--windowed",
    # "--console",
    "--name=inRat planner v1.0.0",
    "--clean",
    "--icon=src/resources/images/icon.ico",
])