from setuptools import setup

setup(
    name='broadcast-logging',
    version='0.1',

    description='A Python logging system handler which broadcasts log '
                'messages and a matching receiver executable.',
    author='Johannes Wienke',
    author_email='languitar@semipol.de',
    url='https://github.com/languitar/broadcast-logging',
    license='LPGLv3+',

    py_modules=['broadcastlogging']
)
