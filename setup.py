import sys
from setuptools import setup

setup(
    name='pyweixin',
    version='2.0.0',
    author='Hello-Mr-Crab',
    author_email='3083256475@qq.com',
    classifiers=[
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    platforms=["Windows"],
    description='A Powerful Windows-PC-WeChat 4.1+ automation Tool',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',  
    url='https://github.com/Hello-Mr-Crab/pywechat',
    packages=['pyweixin'],
    license='LGPL',
    keywords=['rpa', 'windows', 'wechat', 'automation', 'wechat4.1'],
    python_requires='>=3.9',
    install_requires=[
        'emoji>=2.14.1',
        'PyAutoGUI>=0.9.54',
        'pycaw>=20240210',
        'pywin32>=308',
        'pywin32-ctypes>=0.2.2',
        'pywinauto>=0.6.8',
        'psutil>=5.9.5',
        'pillow>=10.4.0'
    ]
)

'''
Author: Hello-Mr-Crab
Contributor: Viper, Chanpoe, mrhan1993, nmhjklnm, clen1, guanjt3
Note: This version only supports WeChat 4.1+
'''
