from os.path import abspath, dirname, join
from setuptools import find_packages, setup


ENTRY_POINTS = '''
[paste.app_factory]
main = asset_tracker:main
'''
APPLICATION_CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Pyramid',
    'Framework :: Pyramid :: InvisibleRoads',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
]
APPLICATION_REQUIREMENTS = [
    # architecture
    'invisibleroads-posts >= 0.7.4',
    'invisibleroads-records >= 0.5.3',
    # web
    'pyramid',
    # database
    'alembic',
    'sqlalchemy',
    # test
    'pytest',
    # geometry
    'geoalchemy2',
    'geotable',
    'shapely',
    'utm',
    # computation
    'numpy',
    'pandas',
    # shortcut
    'invisibleroads-macros-configuration >= 1.0.3',
]
TEST_REQUIREMENTS = [
    'pytest-cov',
    'webtest',
]
FOLDER = dirname(abspath(__file__))
DESCRIPTION = '\n\n'.join(open(join(FOLDER, x)).read().strip() for x in [
    'README.md', 'CHANGES.md'])


setup(
    name='asset-tracker',
    version='0.0.5',
    description='Asset Tracker',
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    classifiers=APPLICATION_CLASSIFIERS,
    author='CrossCompute Inc.',
    author_email='support@crosscompute.com',
    url='https://assets.publicpower.org',
    keywords='web wsgi bfg pylons pyramid invisibleroads',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={'test': TEST_REQUIREMENTS},
    install_requires=APPLICATION_REQUIREMENTS,
    entry_points=ENTRY_POINTS)
