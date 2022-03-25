import os
from setuptools import setup, find_packages


version = "0.1.dev0"

install_requires = [
    'frozen_box',
    'frozendict',
    'horseman',
    'http-session >= 0.2',
    'importscan',
    'prejudice',
    'roughrider.cors',
    'roughrider.routing',
    'transaction',
]

test_requires = [
    'WebTest',
    'pytest',
    'smtpdfix',
    'sqlalchemy.orm',
    'zope.sqlalchemy',
]


setup(
    name='kavallerie',
    version=version,
    author='Novareto GmbH & Souheil Chelfouh',
    author_email='',
    url='https://github.com/HorsemanWSGI/kavallerie',
    download_url='http://pypi.python.org/pypi/kavallerie',
    description='Full-blown WSGI Framework using Horseman.',
    long_description=(open("README.rst").read() + "\n" +
                      open(os.path.join("docs", "HISTORY.rst")).read()),
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    setup_requires=[],
    tests_require=test_requires,
    extras_require={
        'test': test_requires,
    }
)
