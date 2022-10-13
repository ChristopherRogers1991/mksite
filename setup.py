from setuptools import setup, find_packages

setup(
    name='mksite',
    version='0.0.1',
    packages=find_packages(where="src"),
    package_dir={"" : "src"},
    package_data={'mksite.resources':['*']},
    url='',
    license='',
    author='chris',
    author_email='',
    description=''
)
