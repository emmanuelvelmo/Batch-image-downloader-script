from cx_Freeze import setup, Executable

setup(name="Batch image downloader", executables=[Executable("Batch image downloader script.py")], options={"build_exe": {"excludes": ["tkinter"]}})