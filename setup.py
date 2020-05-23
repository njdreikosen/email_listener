from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='email_listener',
    version='0.3',
    description='Listen in an email folder and process incoming emails.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications :: Email',
    ],
    url='https://github.com/njdreikosen/email_listener',
    author='Noah Dreikosen',
    author_email='ndreikosen@gmail.com',
    license='GNU GPLv3',
    packages=['email_listener'],
    install_requires=[
        'datetime',
        'email',
        'html2text',
        'imapclient',
        'pytest',
    ],
    zip_safe=False)

