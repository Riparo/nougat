from setuptools import setup
from os import path
from nougat import __version__
from distutils.errors import DistutilsPlatformError

here = path.abspath(path.dirname(__file__))


setup_kwargs = {
    'name': 'nougat',
    'version': __version__,
    'description': 'Async API framework with human friendly params definition and automatic document',
    'url': 'https://github.com/Kilerd/nougat',

    'author': 'Kilerd Chan',
    'author_email': 'blove694@gmail.com',

    'license': 'MIT',

    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    'keywords': 'web framework async',

    'packages': ['nougat'],
    'install_requires': [
        'httptools>=0.0.9',
        'uvloop>=0.8.0',
        'aiofiles>=0.3.0',
        'aiohttp>=2.0.7',
        'toml>=0.9.2'
    ],
}
try:
    setup(**setup_kwargs)

except DistutilsPlatformError as exception:

    setup_kwargs['install_requires'].remove('uvloop>=0.8.0')
    setup(**setup_kwargs)
