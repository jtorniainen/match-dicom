from setuptools import setup

setup(name='match-dicom',
      version='0.1',
      description='Simple, command-line DICOM-RAW matcher',
      author='jtorniainen, Biophysics of Bone and Cartilage, Department of Applied Physics, University of Eastern Finland',
      url='https://github.com/jtorniainen/match-dicom',
      license='MIT',
      packages=['match-dicom'],
      package_dir={'match-dicom': 'match-dicom'},
      include_package_data=False,
      install_requires=['blessings>=1.6',
                        'pydicom>=0.9.9',
                        'tifffile>=0.10.0'],
      entry_points={"console_scripts":
                    ["match-dicom = match-dicom.match-dicom:run_from_cli"]})
