from setuptools import setup, find_packages
import os.path
__version__ = open(os.path.join(os.path.dirname(__file__),
                                "second_hand_songs_wrapper/VERSION")).read().strip()

setup(name='second_hand_songs_wrapper',
      version=__version__,
      description="An API wrapper for second hand song db",
      long_description=open("./README.md", "r").read(),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
      keywords='second hand songs, api wrapper, song covers, music',
      author='Roman A. Taycher',
      author_email='rtaycher1987@gmail.com',
      url='http://crouchofthewildtiger.com/',
      license='MIT License',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=["voluptuous==0.4", "docopt==0.5"],
      test_suite="nose.collector",
      tests_require=['nose'],
      entry_points="""
# -*- Entry points: -*-
[console_scripts]
second_hand_songs_api_cmdline=bin.second_hand_songs_api_cmdline:main
""",
      )
