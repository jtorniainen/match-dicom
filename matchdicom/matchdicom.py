#!/usr/bin/env python3

import dicom
import os
import sys
# import argparse
import tifffile
import blessings

# Maps DICOM files to RAW files using timestamps
# Usage: ./map_dicom DICOM_FILE DIRECTORY
#
# Script will print out files in the target directory that contain a matching timestamp.
#
# jtorniainen
# UEF 2017, MIT License

term = blessings.Terminal()


def read_dicom_comment(dicom_file):
    """ Returns the contents of the comment field of a dicom file. """
    if hasattr(dicom_file, 'ImageComments'):
        return dicom_file.ImageComments
    else:
        return None


def read_dicom_comments(path):
    """ Reads comments from all files found in path """

    if os.path.isdir(path):
        dicom_filenames = os.listdir(path)
        for dicom_filename in dicom_filenames:
            dicom_file = dicom.read_file(os.path.join(path, dicom_filename))
            print(read_dicom_comment(dicom_file))
    else:
        print(read_dicom_comment(dicom.read_file(path)))


def match_timestamp(directory, target):
    for f in os.listdir(directory):
        if f.endswith('.oct'):
            tfile = tifffile.TiffFile(os.path.join(directory, f))
            timestamp = tfile.pages[0].tags['datetime'].value.decode('ascii')
            if timestamp == target:
                print(term.green_bold('{} = {}\t'.format(target, timestamp)) + f)
            else:
                print('{} ≠ {}'.format(target, timestamp))


def read_dicom_timestamp(dicom_file):
    datetime_str = '{}:{}:{} {}:{}:{}'.format(dicom_file.AcquisitionDate[0:4],
                                              dicom_file.AcquisitionDate[4:6],
                                              dicom_file.AcquisitionDate[6:8],
                                              dicom_file.AcquisitionTime[0:2],
                                              dicom_file.AcquisitionTime[2:4],
                                              dicom_file.AcquisitionTime[4:6])

    return datetime_str


def run_from_cli():
    if len(sys.argv) == 2:  # Single file -> attempt to read and display DICOM comment
        try:
            dicom_file = dicom.read_file(sys.argv[1])
            print(read_dicom_comment(dicom_file))
        except dicom.errors.InvalidDicomError:
            print('{} appears not to be a DICOM-file.')

    elif len(sys.argv) == 3:  # Two files -> see which case
        print('Not implemented yet!')
    else:
        print('match-dicom takes exactly TWO input arguments! ')


# if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('dicom', help='path to a DICOM file')
    # parser.add_argument('directory', help='path to RAW files')
    # args = parser.parse_args()
    # timestamp = read_timestamp(args.dicom)
    # match_timestamp(args.directory, timestamp)
