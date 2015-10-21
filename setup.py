from setuptools import setup, find_packages

version = '1.0.6'

setup(
  name='mashape-analytics',
  version=version,
  description='Python Agent for Mashape Analytics',
  author='Mashape',
  author_email='opensource@mashape.com',
  url='https://github.com/Mashape/analytics-agent-python',
  download_url = 'https://github.com/Mashape/analytics-agent-python/archive/v{0}.zip'.format(version),
  license='MIT',
  packages=find_packages(exclude=['tests']),
  zip_safe=False,
  install_requires=[
    'pytz==2015.2',
    'pyzmq==14.5.0',
    'six==1.9.0',
    'ujson==1.33'
  ],
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
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
  ]
)
