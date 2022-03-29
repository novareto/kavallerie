from setuptools import setup


setup(
    name='kavallerie',
    install_requires = [
        'frozen_box',
        'horseman',
        'http-session >= 0.2',
        'importscan',
        'itsdangerous',
        'prejudice',
        'roughrider.cors',
        'roughrider.routing',
        'transaction',
        'zope.interface',
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
