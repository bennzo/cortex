from setuptools import setup, find_packages

setup(
    name='cortex',
    version='1.0',
    description='Brain-Computer interface',
    author='Ben Ohayon',
    author_email='bennohay@gmail.com',
    url='https://github.com/bennzo/cortex',
    packages=find_packages(),
    install_requires=['bson', 'Click', 'Flask', 'furl', 'numpy', 'pika', 'Pillow',
                      'protobuf', 'pymongo', 'pytest', 'requests', 'mongomock', 'pytz', 'Sphinx'],
    python_requires='>=3.8'
)
