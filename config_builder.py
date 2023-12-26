import configparser
import chardet


config = configparser.ConfigParser()
config['Application'] = {
    'name': "Thrust Accounting",
    'version': '1.0',
    'entry_point': 'src.server:run',
    'console': 'true'
}

config['Python'] = {
    'version': '3.11.1'
}

encoding = None

with open('./src/requirements.txt', 'rb') as f:
    encoding = chardet.detect(f.read())

print(encoding)

with open('./src/requirements.txt', 'r', encoding=encoding.get('encoding', 'utf-8')) as f:
    data = f.read()
    config['Include'] = {
        'pypi_wheels': data,
        'extra_wheel_sources': 'wheels/'
    }


with open("installer.cfg", "w") as configfile: 
    config.write(configfile)