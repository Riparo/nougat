from setuptools import setup
from os import path
from nougat import __version__

here = path.abspath(path.dirname(__file__))

setup(
    name='nougat',
    version=__version__,
    description='Async API framework',
    url='https://github.com/NougatWeb/nougat',

    author='Kilerd Chan',
    author_mail='blove694@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='web framework async',

    packages=['nougat'],

    install_requires=[
        'aiohttp',
        'httptools',
        'yarl>=0.13.0',
        'toml>=0.9.4',
        'fire>=0.1.3',
        'watchdog>=0.8.3',
        'websockets',

    ],
    entry_points='''
        [console_scripts]
        nougat=nougat.cli:main
    ''',
    python_requires='>=3.6',
)

