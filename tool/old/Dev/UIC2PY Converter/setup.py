from _property_ import __getMetaProperty
from distutils.core import setup
import py2exe

setup(
    windows=['main.py'],
    name='noolsab',
    version=__getMetaProperty('VERSION'),
    packages=[''],
    url='nooslab.com',
    license='',
    author='nooslab',
    author_email='',
    description='UIC2PY Converter'
)
