from setuptools import setup, find_packages

version = '1.1.0'

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
    'pytz==2016.4',
    'requests==2.9.1',
    'six==1.10.0',
    'ujson==1.35',
    'Werkzeug==0.11.9',
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
  ],
  entry_points={
    'paste.filter_app_factory': [
      'mashape_analytics = mashapeanalytics:make_wsgi_app',
    ],
  }
)
