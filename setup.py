from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='django-preflight-checks',
    version='0.1.0b1',
    url='http://github.com/bpeschier/django-preflight',
    author="Bas Peschier",
    author_email="bpeschier@fizzgig.nl",
    packages=['preflight', ],
    license='MIT',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['Django>=1.8.dev0'],
    test_requires=[
        'django-debug-toolbar>=1.0',
    ]
)