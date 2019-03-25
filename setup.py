from os.path import abspath, dirname, join
from setuptools import find_packages, setup


ENTRY_POINTS = """
[console_scripts]
initialize_asset_tracker_db=asset_tracker.scripts.initialize_db:main
[paste.app_factory]
main = asset_tracker:main
"""
APP_CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Pyramid',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
]
APP_REQUIREMENTS = [
    # Web
    'plaster_pastedeploy',
    'pyramid',
    'pyramid_jinja2',
    'pyramid_debugtoolbar',
    'waitress',
    # Database
    'alembic',
    'pyramid_retry',
    'pyramid_tm',
    'sqlalchemy',
    'transaction',
    'zope.sqlalchemy',
]
TEST_REQUIREMENTS = [
    'pytest >= 3.7.4',
    'pytest-cov',
    'webtest >= 1.3.1',
]
FOLDER = dirname(abspath(__file__))
DESCRIPTION = '\n\n'.join(open(join(FOLDER, x)).read().strip() for x in [
    'README.rst', 'CHANGES.rst'])


setup(
    name='asset_tracker',
    version='0.1',
    description='Asset Tracker',
    long_description=DESCRIPTION,
    classifiers=APP_CLASSIFIERS,
    author='CrossCompute Inc.',
    author_email='support@crosscompute.com',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={'testing': TEST_REQUIREMENTS},
    install_requires=APP_REQUIREMENTS,
    entry_points=ENTRY_POINTS)
