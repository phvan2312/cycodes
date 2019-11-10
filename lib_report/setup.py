from setuptools import setup, find_packages
import os

setup(
    name='lib-report',
    version='0.1.0',
    description='report',
    author='Cinnamon AI Labs',
    url='http://cinnnamon.is',
    packages=find_packages(exclude=('tests', 'docs')),
    package_data={"report": [os.path.join('tool', 'correct_dictionary.json')]},
    include_package_data=True,
    python_requires=">=3.5",
)