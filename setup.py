import os
import sys

from setuptools import setup, find_packages

requires = [
    'flask-async',
    'docopt',
    'pprintpp',
]

if sys.version_info[:3] < (3, 3):
    raise SystemError('Python 3.3+ required')

setup_args = dict(
    name='galerka',
    version='0.0',
    description='galerka',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
    author='Petr Viktorin',
    author_email='encukou@gmail.com',
    url='',
    packages=['galerka'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)

if __name__ == '__main__':
    setup(**setup_args)
