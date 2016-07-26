from setuptools import setup

setup(name='getorg',
      version='0.1.9',
      description='For mapping contributors to GitHub organizations',
      url='http://github.com/getorg/getorg',
      author='Stuart Geiger',
      author_email='stuart@stuartgeiger.com',
      license='MIT',
      packages=['getorg'],
      install_requires=[
          'pygithub', 'ipywidgets', 'geopy', 'datetime'],
      zip_safe=False)
