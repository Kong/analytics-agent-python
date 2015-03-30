import io

from setuptools import setup, find_packages

setup(
  name='apianalytics',
  version='1.0.0',
  description='',
  long_description=io.open('README.md', encoding='utf-8').read(),
  author='Kenneth Lee',
  author_email='kennethkl@gmail.com',
  url='https://github.com/Mashape/analytics-agent-python',
  license='MIT',
  packages=find_packages(exclude=['tests']),
  zip_safe=False,
  install_requires=[line.strip('\n') for line in io.open('requirements.txt', encoding='utf-8').readlines()],
  include_package_data=True,
  classifiers=[
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules'
    'Topic :: Utilities',
  ]
)
