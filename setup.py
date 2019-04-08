from setuptools import setup

setup(
    name = 'hertz',
    version = '0.1.0',
    packages = ['hertz'],
    install_requires = [
        'simpleaudio>=1.0',
        'numpy>=1.16',
        'matplotlib>=3.0',
	'pandas>=0.24'
    ],
    entry_points = {
        'console_scripts': [
            'hertz = hertz.__main__:main'
        ]
    })
