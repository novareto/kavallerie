from setuptools import setup


setup(
    name='kavallerie',
    install_requires = [
        'frozen_box',
        'horseman >= 0.6',
        'http-session >= 0.2',
        'importscan',
        'itsdangerous',
        'prejudice',
        'roughrider.cors',
        'roughrider.routing',
        'transaction',
        'zope.interface',
        'frozendict',
    ],
    extras_require={
        'test': [
            'WebTest',
            'pytest',
            'smtpdfix',
            'frozendict',
            'sqlalchemy.orm',
            'zope.sqlalchemy',
        ]
    }
)
