from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='email_listener',
    version='0.1',
    description='',
    long_description=long_description,
    long_description_content_type=text/markdown,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Communications :: Email',
    ]
    url='',
    author='Noah Dreikosen',
    author_email='ndreikosen@gmail.com',
    license='GNU GPLv3',
    packages=['email_listener'],
    install_requires=[
        'email',
        'html2text',
        'imapclient',
        'os',
        'datetime',
    ],
    zip_safe=False)

