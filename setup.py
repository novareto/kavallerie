from setuptools import setup


setup(
    name='kavallerie',
    install_requires = [
        'frozen_box',
        'frozendict',
        'horseman >= 0.6',
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
            'pyhamcrest',
            'smtpdfix',
            'sqlalchemy.orm',
            'zope.sqlalchemy',
        ]
    }
)
