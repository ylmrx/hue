from setuptools import setup

setup(
    name='fhuezz',
    version='0.0.1',
    py_modules=['fhuezz'],
    install_requires=[
        'requests',
        'jq',
        'pygments',
        'ipaddress',
        'click'
    ],
    entry_points='''
        [console_scripts]
        fhuezz=fhuezz:cli
    ''',
    author='Yoann Lamouroux',
    author_email='ylamouroux@ubuntu.com'
)
