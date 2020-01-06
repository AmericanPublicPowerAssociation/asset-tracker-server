import os

from setuptools import setup, find_packages

requires = [
    'plaster_pastedeploy',
    'pyramid',
    'pyramid_debugtoolbar',
    'waitress',
]

setup(
    name='dss-server',
    version='0.1',
    description='DSS Server',
    author='Miguel G.',
    author_email='miguel.gordian@devlabs.com.mx',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = dss_server:main',
        ],
    },
)