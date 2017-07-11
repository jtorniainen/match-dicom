from setuptools import setup

setup(name='matchdicom',
      version='0.2',
      description='Simple, command-line DICOM-RAW matcher',
      author='jtorniainen, Biophysics of Bone and Cartilage, Department of Applied Physics, University of Eastern Finland',
      url='https://github.com/jtorniainen/matchdicom',
      license='MIT',
      packages=['matchdicom'],
      package_dir={'matchdicom': 'matchdicom'},
      include_package_data=False,
      install_requires=['blessings>=1.6',
                        'pydicom>=0.9.9',
                        'tifffile>=0.10.0',
                        'logzero>=1.2.1'],
      entry_points={"console_scripts":
                    ["match-dicom = matchdicom.matchdicom:run_from_cli"]})
