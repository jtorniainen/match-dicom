#!/usr/bin/env python3

import dicom
import os
import sys
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


def _get_dicom_comment(dicom_file):
    """ Returns the contents of the comment field of a dicom file """
    if hasattr(dicom_file, 'ImageComments'):
        return dicom_file.ImageComments
    else:
        return None


def _get_dicom_timestamp(dicom_file):
    if hasattr(dicom_file, 'AcquisitionDate'):
        datetime_str = '{}:{}:{} {}:{}:{}'.format(dicom_file.AcquisitionDate[0:4],
                                                  dicom_file.AcquisitionDate[4:6],
                                                  dicom_file.AcquisitionDate[6:8],
                                                  dicom_file.AcquisitionTime[0:2],
                                                  dicom_file.AcquisitionTime[2:4],
                                                  dicom_file.AcquisitionTime[4:6])

    else:
        datetime_str = None
    return datetime_str


def _print_dicom(filename, comment, timestamp):
    """ Pretty print the indentifiers of a DICOM file """

    if not comment:
        comment = '<None>'

    if not timestamp:
        timestamp = '<None>'

    dicom_str = (filename.ljust(20) +
                 term.magenta_bold(comment).ljust(30) +
                 term.yellow(timestamp).ljust(40))
    print(dicom_str)


def read_dicom_comments(path):
    """ Reads comments from all files found in path """

    print('FILE'.ljust(20) + 'COMMENT'.ljust(30) + 'TIME'.ljust(40))

    if os.path.isdir(path):
        dicom_filenames = os.listdir(path)
        for dicom_filename in dicom_filenames:
            dicom_file = dicom.read_file(os.path.join(path, dicom_filename))
            dicom_comment = _get_dicom_comment(dicom_file)
            dicom_timestamp = _get_dicom_timestamp(dicom_file)
            _print_dicom(dicom_filename, dicom_comment, dicom_timestamp)
    else:
        dicom_file = dicom.read_file(path)
        dicom_comment = _get_dicom_comment(dicom_file)
        dicom_timestamp = _get_dicom_timestamp(dicom_file)
        _print_dicom(path, dicom_comment, dicom_timestamp)


def match_timestamp(directory, target):
    for f in os.listdir(directory):
        if f.endswith('.oct'):
            tfile = tifffile.TiffFile(os.path.join(directory, f))
            timestamp = tfile.pages[0].tags['datetime'].value.decode('ascii')
            if timestamp == target:
                print(term.green_bold('{} = {}\t'.format(target, timestamp)) + f)
            else:
                print('{} ≠ {}'.format(target, timestamp))


def run_from_cli():
    if len(sys.argv) == 2:  # Single file -> attempt to read and display DICOM comment
        try:
            read_dicom_comments(sys.argv[1])
        except dicom.errors.InvalidDicomError:  # FIXME wrong place to catch this
            print('{} appears not to be a DICOM-file.'.format(sys.argv[1]))

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
