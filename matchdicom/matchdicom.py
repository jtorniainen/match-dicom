#!/usr/bin/env python3

import dicom
import os
import sys
import argparse
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


def read_comment(dicom_filename):
    """ Returns the contents of the comment field of a dicom file. """
    dicom_data = dicom.read_file(dicom_filename)
    if hasattr(dicom_data, 'ImageComments'):
        return dicom_data.ImageComments
    else:
        return None


def read_comments(path):
    """ Reads comments from all files found in path """

    if os.path.isdir(path):
        dicom_filenames = os.listdir(path)
        for dicom_filename in dicom_filenames:
            print(read_comment(os.path.join(path, dicom_filename)))
    else:
        print(read_comment(path))


def match_timestamp(directory, target):
    for f in os.listdir(directory):
        if f.endswith('.oct'):
            tfile = tifffile.TiffFile(os.path.join(directory, f))
            timestamp = tfile.pages[0].tags['datetime'].value.decode('ascii')
            if timestamp == target:
                print(term.green_bold('{} = {}\t'.format(target, timestamp)) + f)
            else:
                print('{} ≠ {}'.format(target, timestamp))


def read_timestamp(filename):
    dfile = dicom.read_file(filename)
    datetime_str = '{}:{}:{} {}:{}:{}'.format(dfile.AcquisitionDate[0:4],
                                              dfile.AcquisitionDate[4:6],
                                              dfile.AcquisitionDate[6:8],
                                              dfile.AcquisitionTime[0:2],
                                              dfile.AcquisitionTime[2:4],
                                              dfile.AcquisitionTime[4:6])

    return datetime_str


def run_from_cli():
    if len(sys.argv) == 2:  # Single file -> attempt to read and display DICOM comment
        print(read_comment(sys.argv[1]))
    elif len(sys.argv) == 3:  # Two files -> see which case
        print('Not implemented yet!')
    else:
        print('match-dicom takes exactly TWO input arguments! ')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dicom', help='path to a DICOM file')
    parser.add_argument('directory', help='path to RAW files')
    args = parser.parse_args()
    timestamp = read_timestamp(args.dicom)
    match_timestamp(args.directory, timestamp)
