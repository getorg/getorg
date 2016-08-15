from setuptools import setup

setup(name='getorg',
      version='0.3.0',
      description='Information and analytics about GitHub organizations',
      url='http://github.com/getorg/getorg',
      author='Stuart Geiger',
      author_email='stuart@stuartgeiger.com',
      license='MIT',
      packages=['getorg'],
      install_requires=[
          'pygithub', 'geopy', 'retrying'],
      zip_safe=False)
