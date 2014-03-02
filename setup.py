import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.markdown')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-binder',
    version='0.1',
    packages=['binder'],
    include_package_data=True,
    license='BSD License',
    description='A simple Django app to manage your BIND DNS zones.',
    long_description=README,
    author='Jeffrey Forman',
    author_email='code@jeffreyforman.net',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
