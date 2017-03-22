#!/usr/bin/env python3

import dicom
import os
import sys
import tifffile
import blessings
import datetime
import argparse

# Maps DICOM files to RAW files using timestamps
# Usage: ./map-dicom DICOM RAW
#
# Script will print out files in the target directory that contain a matching timestamp.
#
# jtorniainen
# UEF 2017, MIT License

# TODO: convert time stamps to datetimes instead of strings


term = blessings.Terminal()


def _check_match(dicom_file, raw_file):
    """ Check if the timestamp of a DICOM file matches the timestamp of a RAW file """
    timestamp_dicom = _get_dicom_timestamp(dicom_file)
    timestamp_raw = _get_raw_timestamp(raw_file)
    return timestamp_dicom == timestamp_raw


def _find_matching_files(dicom_file, raw_dir, verbose=False):
    """ Searches a directory for matching RAW files """
    raw_filenames = os.listdir(raw_dir)
    target_time = _get_dicom_timestamp(dicom_file)
    matches = []
    for raw_filename in raw_filenames:
            try:
                raw_file = tifffile.TiffFile(os.path.join(raw_dir, raw_filename))
                raw_timestamp = _get_raw_timestamp(raw_file)

                if verbose:
                    print(term.yellow_bold('Checking: ') + '{} vs. {} ({})'.format(target_time,
                                                                                   raw_timestamp,
                                                                                   raw_filename))

                if target_time == raw_timestamp:
                    print(term.green_bold('Found: ') + '{} is a match'.format(raw_filename))
                    matches.append(raw_filename)

            except ValueError:
                print(term.red_bold('Warning: ') + '{} is not a TIFF file (skipped)'.format(raw_filename))
    return matches


def match_directories(dicom_dir, raw_dir):
    """ Finds matching files in two directories (one DICOM and one RAW) """
    matches = {}
    dicom_filenames = os.listdir(dicom_dir)
    for dicom_filename in dicom_filenames:
        try:
            dicom_file = dicom.read_file(os.path.join(dicom_dir, dicom_filename), stop_before_pixels=True)
            matches[dicom_filename] = _find_matching_files(dicom_file, raw_dir)
        except dicom.errors.InvalidDicomError:
            print(term.red_bold('WARNING: ') + '{} is not a DICOM-file!'.format(dicom_filename).rjust(20))
            continue
    return matches


def _get_dicom_comment(dicom_file):
    """ Returns the contents of the comment field of a dicom file """
    if hasattr(dicom_file, 'ImageComments'):
        return dicom_file.ImageComments
    else:
        return None


# -------------------- FILE HANDLERS --------------------

def open_dicom(path):
    return dicom.read_file(path, stop_before_pixels=True)


def open_raw(path):
    return tifffile.TiffFile(path)

# TIMESTAMPS


def _get_raw_timestamp(raw_file):
    """ Returns the timestamp of the raw file """
    timestamp_str = raw_file.pages[0].tags['datetime'].value.decode('ascii')
    return datetime.datetime.strptime(timestamp_str, '%Y:%m:%d %H:%M:%S')


def _get_dicom_timestamp(dicom_file):  # FIXME: convert to datetime
    """ Gets the timestamp from a DICOM file """
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


# PRINTING FUNCTIONS

def _print_metadata(filename, comment, timestamp):
    """ Pretty print the metadata of a DICOM/RAW file """

    if not comment:
        comment = '<None>'

    if not timestamp:
        timestamp = '<None>'
    else:
        timestamp = str(timestamp)

    print(filename.ljust(60) + term.magenta_bold(comment).ljust(60) + term.yellow(timestamp))


def print_dicom_metadata(path):
    """ Reads comments and timestamps from all DICOM files found in path """

    if os.path.isdir(path):
        for dicom_filename in os.listdir(path):
            try:
                dicom_file = open_dicom(os.path.join(path, dicom_filename))
                dicom_comment = _get_dicom_comment(dicom_file)
                dicom_timestamp = _get_dicom_timestamp(dicom_file)
                _print_metadata(dicom_filename, dicom_comment, dicom_timestamp)

            except dicom.errors.InvalidDicomError:
                print(term.red_bold('WARNING:') + '{} not DICOM'.format(dicom_filename).ljust(20))
                continue

            except IsADirectoryError:
                print(term.red_bold('WARNING:') + '{} is a directory'.format(dicom_filename).ljust(20))
                continue
    else:
        try:
            dicom_file = open_dicom(path)
            dicom_comment = _get_dicom_comment(dicom_file)
            dicom_timestamp = _get_dicom_timestamp(dicom_file)
            _print_metadata(path, dicom_comment, dicom_timestamp)

        except dicom.errors.InvalidDicomError:
            print(term.red_bold('WARNING:').ljust(20) + '{} not DICOM'.format(path))


def print_raw_metadata(path):
    """ Reads comments and timestamps from all RAW files found in path """

    if os.path.isdir(path):
        for raw_filename in os.listdir(path):
            try:
                raw_file = open_raw(os.path.join(path, raw_filename))
                raw_comment = ''
                raw_timestamp = _get_raw_timestamp(raw_file)
                _print_metadata(raw_filename, raw_comment, raw_timestamp)

            except dicom.errors.InvalidDicomError:
                print(term.red_bold('WARNING:') + '{} not DICOM'.format(raw_filename).ljust(20))
                continue
    else:
        try:
            raw_file = open_raw(path)
            raw_comment = ''
            raw_timestamp = _get_raw_timestamp(raw_file)
            _print_metadata(path, raw_comment, raw_timestamp)

        except dicom.errors.InvalidDicomError:
            print(term.red_bold('WARNING:').ljust(20) + '{} not DICOM'.format(path))


def print_matching_files(matches):
    """ Pretty print matches-dict """
    for key, value in matches.items():
        print(term.bold_yellow(key).ljust(40) + ' -> ' + term.green(str(value)))


# MAIN--------------------------------------------------

def run_from_cli():

    parser = argparse.ArgumentParser()
    parser.add_argument('targets', nargs='*')
    parser.add_argument('-r', help='Access meta-data of RAW files', action='store_true')
    args = parser.parse_args()

    if len(args.targets) == 1:  # Single file or directory
        if args.r:
            print_raw_metadata(args.targets[0])
        else:
            print_dicom_metadata(args.targets[0])

    elif len(sys.argv) == 3:  # Two files (this branch is probably now broken)

        if os.path.isdir(sys.argv[1]) and os.path.isdir(sys.argv[2]):  # both dirs
            matches = match_directories(sys.argv[1], sys.argv[2])
            print_matching_files(matches)

        elif os.path.isdir(sys.argv[2]):  # dicom input is file -> raw input is dir
            dicom_file = dicom.read_file(sys.argv[1], stop_before_pixels=True)
            _find_matching_files(dicom_file, sys.argv[2], verbose=True)

        else:  # both inputs are files
            dicom_file = dicom.read_file(sys.argv[1], stop_before_pixels=True)
            raw_file = tifffile.TiffFile(sys.argv[2])
            check_result = _check_match(dicom_file, raw_file)

            if check_result:
                print(term.green_bold('Match found'))
            else:
                print(term.red_bold('No match found'))

    else:
        print('match-dicom takes exactly TWO input arguments! ')
