from setuptools import find_packages, setup

setup(
    name='smarthome',
    version='0.3.0',
    author='themylogin',
    author_email='themylogin@gmail.com',
    packages=find_packages(exclude=["tests"]),
    scripts=[],
    test_suite="nose.collector",
    url='http://github.com/themylogin/smarthome',
    description='Smart home daemon',
    long_description=open('README.md').read(),
    install_requires=[
        "lxml",
        "paramiko",
        "pyparallel",
        "pyserial",
        "werkzeug",
        "pyephem",
    ],
    setup_requires=[
        "nose>=1.0",
    ],
)
