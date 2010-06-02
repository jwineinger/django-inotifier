from setuptools import setup

f = open('README')
readme = f.read()
f.close()

setup(
    name='django-inotifier',
    version='0.9.0',
    description='django-inotifier is a reusable application which provides a thin django signals wrapper around pyinotify.',
    long_description=readme,
    author='Jay Wineinger',
    author_email='jay.wineinger@gmail.com',
    url='http://github.com/jwineinger/django-inotifier/tree/master',
    packages=['inotifier',],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: Linux',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    install_requires=['pyinotify',],
    zip_safe=False,
)
