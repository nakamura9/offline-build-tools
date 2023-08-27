import configparser

config = configparser.ConfigParser()
config['Application'] = {
    'name': "Bench Business Tools",
    'version': '2.0',
    'entry_point': 'myapp:main'
}

config['Python'] = {
    'version': '3.11.1'
}

with open('bench_requirements.txt', 'r', encoding='utf-8') as f:
    data = f.read()
    config['Include'] = {
        'pypi_wheels': data,
        'extra_wheel_sources': 'wheels/'
    }


with open("installer2.cfg", "w") as configfile: 
    config.write(configfile)