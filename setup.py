import os
from setuptools import find_packages, setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='StockTalk',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Utilizing social media api and stock data, we convieniently \
                present opinion on the top movers of stocks.',
    url='https://stock-talk.herokuapp.com/',
    author='Norton Pengra, Jeremy Edwards, Rick Tesmond, and Kent Ross',
    author_email='',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9.4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=['django'],
    extras_requires={'tests': ['pytest', 'pytest-cov', 'tox']},
)
