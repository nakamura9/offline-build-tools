# Instructions 

- Install NSIS 
    `https://nsis.sourceforge.io/Download`
- Create virtualenv
    `python -m venv env`
    `env/scripts/activate`
    `pip install pynsist`
- make sure pip setuptools and wheel are up to date
    `python.exe -m pip install --upgrade pip setuptools wheel`
- Make sure microsoft build tools for C++ are installed and up to date
- Generate cfg using config_builder
    `python config_builder.py`
- use the wheels folder to install alternative wheels for packages without them
- generate an installer using the following command:
    `pynsist installer.cfg`
- if it fails because of a missing wheel, build manually using 
    `pip wheel --wheel-dir wheels/ package_name==version`
- Some packages may use deprecated features and are not actively maintained. Use 
    `python setup.py bdist_wheel` 
    to compile wheels from source 
    especially for Pygal and django formtools.
- add these custom built wheels to your wheels folder in the root of your project.


# Project structure 
```
|_bench_2
    |
    |_____launcher
    |   |___________launcher.py
    |
    |_____server
        |___________runserver.py
```

