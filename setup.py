from os.path import abspath, dirname, join
from setuptools import find_packages, setup


ENTRY_POINTS = '''
[paste.app_factory]
main = asset_tracker:main
'''
APP_CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Pyramid',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
]
APP_REQUIREMENTS = [
    # web
    'plaster-pastedeploy',
    'pyramid',
    'pyramid-ipython',
    'waitress',
    # database
    'alembic',
    'pyramid-retry',
    'pyramid-tm',
    'sqlalchemy',
    'transaction',
    'zope.sqlalchemy',
    # time
    'pendulum',
    # table
    'pandas>=0.25.1',
    # geotable
    'geoalchemy2>=0.6.3',
    'shapely',
]
TEST_REQUIREMENTS = [
    'pytest >= 3.7.4',
    'pytest-cov',
    'webtest >= 1.3.1',
]
FOLDER = dirname(abspath(__file__))
DESCRIPTION = '\n\n'.join(open(join(FOLDER, x)).read().strip() for x in [
    'README.md', 'CHANGES.md'])


setup(
    name='asset-tracker',
    version='0.0.2',
    description='Asset Tracker',
    long_description=DESCRIPTION,
    classifiers=APP_CLASSIFIERS,
    author='CrossCompute Inc.',
    author_email='support@crosscompute.com',
    url='https://crosscompute.com',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={'testing': TEST_REQUIREMENTS},
    install_requires=APP_REQUIREMENTS,
    entry_points=ENTRY_POINTS)
