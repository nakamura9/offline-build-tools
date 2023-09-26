import configparser

config = configparser.ConfigParser()
config['Application'] = {
    'name': "Bench Business Tools",
    'version': '2.0',
    'entry_point': 'src.server:run',
    'console': 'true'
}

config['Python'] = {
    'version': '3.11.1'
}

with open('./src/requirements.txt', 'r', encoding='utf-16') as f:
    data = f.read()
    config['Include'] = {
        'pypi_wheels': data,
        'extra_wheel_sources': 'wheels/'
    }


with open("installer.cfg", "w") as configfile: 
    config.write(configfile)