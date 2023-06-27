from setuptools import setup

with open('README.md') as f:
    longdesc = f.read()

version = '0.1.0'

config = {
    'description': 'Taxcalc Payroll',
    'url': 'https://github.com/bodiyang/Taxcalc-Payroll',
    'download_url': 'https://github.com/bodiyang/Taxcalc-Payroll',
    'description': 'taxcalcpayroll',
    'long_description': longdesc,
    'version': version,
    'license': 'CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
    'packages': ['taxcalcpayroll'],
    'include_package_data': True,
    'name': 'taxcalcpayroll',
    'install_requires': ['numpy', 'pandas', 'bokeh', 'numba', 'taxcalc'],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    'tests_require': ['pytest'],
    'entry_points': {
        'console_scripts': ['tcp=taxcalcpayroll.tcp:cli_tcp_main']
    }
}

setup(**config)
