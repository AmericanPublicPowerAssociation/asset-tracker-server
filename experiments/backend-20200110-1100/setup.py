from setuptools import setup


requires = [
    'pyramid',
    'waitress',
    'pyramid_tm',
    'sqlalchemy',
    'zope.sqlalchemy'
]

setup(
    name='backend',
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = backend:main'
        ],
        'console_scripts': [
            'initialize_tutorial_db = backend.initialize_db:main'
        ]
    },
)
