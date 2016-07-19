from distutils.core import setup

setup(name='dtrender',
      version='0.1',
      description='Command Line Rendering of Django Templates',
      author='Mark Roddy',
      author_email='markroddy@gmail.com',
      url='http://bitbucket.org/markroddy/dtrender',
      py_modules=['dtrender',],
      scripts=['dtrender',],
      install_requires=["Django==1.2.7"]
           )
