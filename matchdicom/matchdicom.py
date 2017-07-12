#!/usr/bin/env python3

# Maps DICOM files to RAW files using timestamps
# Usage: ./map-dicom DICOM RAW
#
# Script will print out files in the target directory that contain a matching timestamp.
#
# jtorniainen
# UEF 2017, MIT License

import dicom
import os
import tifffile
import blessings
import datetime
import argparse
from logzero import logger, loglevel


term = blessings.Terminal()


def _find_matching_files_raw_to_dicom(raw_file, dicom_dir):
    """ Finds the DICOM file matching the given RAW file.

    Args:
        raw_file <TIFF>: opened RAW-file
        dicom_dir <str>: path to DICOM-files
    Returns:
        matches <list>: list of DICOM-files that match RAW-file
    """

    raw_time = _get_raw_timestamp(raw_file)

    if not raw_time:
        return None

    matches = []

    for dicom_filename in os.listdir(dicom_dir):

        try:

            dicom_file = open_dicom(os.path.join(dicom_dir, dicom_filename))
            dicom_time = _get_dicom_timestamp(dicom_file)

            time_diff = max([dicom_time, raw_time]) - min([dicom_time, raw_time])
            if time_diff.total_seconds() < 2.0:
                matches.append(dicom_filename)
                logger.info('Found matching files')

        except (dicom.errors.InvalidDicomError, IsADirectoryError, TypeError) as error:
            logger.error('Could not open {} [{}]'.format(dicom_filename, error))

    return matches


def _find_matching_files_dicom_to_raw(dicom_file, raw_dir, verbose=False):
    """ Finds the RAW file matching the given DICOM file.

    Args:
        raw_file <TIFF>: opened RAW-file
        dicom_dir <str>: path to DICOM-files
    Returns:
        matches <list>: list of DICOM-files that match RAW-file
    """

    dicom_time = _get_dicom_timestamp(dicom_file)

    if not dicom_time:
        return None

    matches = []
    for raw_filename in os.listdir(raw_dir):
            try:
                raw_file = open_raw(os.path.join(raw_dir, raw_filename))
                raw_time = _get_raw_timestamp(raw_file)

                time_diff = max([dicom_time, raw_time]) - min([dicom_time, raw_time])

                if time_diff.total_seconds() < 2.0:
                    logger.info('Match found')
                    matches.append(raw_filename)

            except (ValueError, IsADirectoryError) as error:
                logger.error('Could not open {} [{}]'.format(raw_filename, error))

    return matches


def match_directories(dicom_dir, raw_dir, verbose=False):
    """ Finds matching all matching files in two directories.

    Args:
        dicom_dir <str>: path to DICOM directory
        raw_dir <str>: path to RAW directory

    Returns:
        matches <dict>: A dict containing all matching files (keys are RAW files, values list of DICOM files)
    """

    matches = {}

    raw_filenames = os.listdir(raw_dir)

    for raw_filename in raw_filenames:
        try:
            raw_file = open_raw(os.path.join(raw_dir, raw_filename))
            matches[raw_filename] = _find_matching_files_raw_to_dicom(raw_file, dicom_dir)

        except (ValueError, IsADirectoryError) as error:
            logger.error('Could not open {} [{}]'.format(raw_filename, error))

    return matches


def _get_dicom_comment(dicom_file):
    """ Returns the contents of the comment field of a DICOM file.

    Args:
        dicom_file <dicom.dataset>: Opened DICOM file

    Returns:
        image_comment <str>: DICOM comment

    """

    if hasattr(dicom_file, 'ImageComments'):
        return dicom_file.ImageComments
    else:
        return None


def open_dicom(path):
    dicom_file = dicom.read_file(path, stop_before_pixels=True)
    return dicom_file


def open_raw(path):
    return tifffile.TiffFile(path)


def _get_raw_timestamp(raw_file):
    """ Returns the time stamp of the RAW file

    Args:
        raw_file <tifffile.TiffFile>: RAW file handler

    Returns:
        timestamp <datetime.datetime> Creation time of the RAW file
    """

    timestamp_str = raw_file.pages[0].tags['datetime'].value.decode('ascii')
    return datetime.datetime.strptime(timestamp_str, '%Y:%m:%d %H:%M:%S')


def _get_dicom_timestamp(dicom_file):
    """ Returns the time stamp of the DICOM file

    Args:
        raw_file <dicom.dataset>: RAW file handler

    Returns:
        timestamp <datetime.datetime> Creation time of the DICOM file
    """

    if hasattr(dicom_file, 'AcquisitionDate'):
        timestamp_str = '{}:{}:{} {}:{}:{}'.format(dicom_file.AcquisitionDate[0:4],
                                                   dicom_file.AcquisitionDate[4:6],
                                                   dicom_file.AcquisitionDate[6:8],
                                                   dicom_file.AcquisitionTime[0:2],
                                                   dicom_file.AcquisitionTime[2:4],
                                                   dicom_file.AcquisitionTime[4:6])

        return datetime.datetime.strptime(timestamp_str, '%Y:%m:%d %H:%M:%S')

    else:
        return None


def _print_metadata(filename, comment, timestamp):
    """ Pretty print the metadata of a DICOM/RAW file.

    Args:
        filename <str>: Name of the file
        comment <str>: Contents of the comment field
        timestamp <datetime.datetime>: Creation timestamp
    """

    if not comment:
        comment = '<None>'

    if not timestamp:
        timestamp = '<None>'
    else:
        timestamp = str(timestamp)

    print(filename.ljust(60) + term.magenta_bold(comment).ljust(60) + term.yellow(timestamp))


def print_dicom_metadata(path):
    """ Reads comments and timestamps from all DICOM files found in given path.

    Args:
        path <str>: Path to target directory
    """

    if os.path.isdir(path):
        filelist = [os.path.join(path, filename) for filename in os.listdir(path)]
    else:
        filelist = [path]

    for dicom_filename in filelist:

        try:
            dicom_file = open_dicom(dicom_filename)
            dicom_comment = _get_dicom_comment(dicom_file)
            dicom_timestamp = _get_dicom_timestamp(dicom_file)
            _print_metadata(dicom_filename, dicom_comment, dicom_timestamp)

        except (dicom.errors.InvalidDicomError, IsADirectoryError) as error:
            logger.error('{} -> {}'.format(dicom_filename, error))


def print_raw_metadata(path):
    """ Reads comments and timestamps from all RAW files found in given path.

    Args:
        path <str>: Path to target directory
    """

    if os.path.isdir(path):
        filelist = [os.path.join(path, filename) for filename in os.listdir(path)]
    else:
        filelist = [path]

    for raw_filename in filelist:
        try:
            raw_file = open_raw(raw_filename)
            raw_comment = ''
            raw_timestamp = _get_raw_timestamp(raw_file)
            _print_metadata(raw_filename, raw_comment, raw_timestamp)

        except (ValueError, IsADirectoryError) as error:
            logger.error('{} -> {}'.format(raw_filename, error))


def print_matching_files(matches):
    """ Pretty print the contents of matches-dict.

    Args:
        matches <dict> Dictionary containing the matching files.
    """
    for key, value in matches.items():
        if value:
            print(key.ljust(35) + ' ↔ ' + term.green(str(value).strip('[').strip(']')))
        else:
            print(key.ljust(35) + ' ↔ ' + term.red(str(value).strip('[').strip(']')))


def print_comparison(dicom_filename, raw_filename):
    """ Print the comparison of meta data of a given DICOM-RAW pair.

    Args:
        dicom_filename <str>: path to DICOM file
        raw_filename <str>: path to RAW file
    """

    try:
        dicom_data = open_dicom(dicom_filename)
        raw_data = open_raw(raw_filename)
    except (dicom.errors.InvalidDicomError, ValueError) as error:
        logger.error('{} {} -> {}'.format(dicom_filename, raw_filename, error))
        return

    dicom_time = _get_dicom_timestamp(dicom_data)
    dicom_comment = _get_dicom_comment(dicom_data)

    raw_time = _get_raw_timestamp(raw_data)

    time_diff = max([dicom_time, raw_time]) - min([dicom_time, raw_time])
    dicom_filename = os.path.basename(dicom_filename)
    raw_filename = os.path.basename(raw_filename)

    name_dicom = dicom_filename.ljust(30)
    name_raw = raw_filename.ljust(30)
    time_raw = term.yellow(str(raw_time))
    time_dicom = term.yellow(str(dicom_time))
    if time_diff.total_seconds() > 2:
        time_diff = ' (Δ=' + term.red(str(time_diff)) + ') '
    else:
        time_diff = ' (Δ=' + term.green(str(time_diff)) + ') '
    comment_dicom = term.magenta(dicom_comment).ljust(45)
    print(name_dicom + comment_dicom + time_dicom + time_diff + time_raw, name_raw)


def run_from_cli():
    """ Command line operation of the module. Can print out metadata of OCT files in a directory or compare files and
        directories. See 'match-dicom --help' for usage.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dicom-path', help='Path to DICOM file or directory')
    parser.add_argument('-r', '--raw-path', help='Path to RAW file or directory')
    parser.add_argument('-v', '--verbose', help='Verbose-mode on', action='store_true')

    args = parser.parse_args()

    if args.verbose:
        loglevel(10)
    else:
        loglevel(100)

    if args.dicom_path and args.raw_path:  # two paths

        if os.path.isdir(args.dicom_path) and os.path.isdir(args.raw_path):  # both paths directories
            logger.debug('Comparing directories')
            matches = match_directories(args.dicom_path, args.raw_path)
            print_matching_files(matches)

        elif os.path.isdir(args.dicom_path):
            raw_file = open_raw(args.raw_path)
            matches = _find_matching_files_raw_to_dicom(raw_file, args.dicom_path)
            print_matching_files(matches)

        elif os.path.isdir(args.raw_path):
            dicom_file = open_dicom(args.dicom_path)
            matches = _find_matching_files_dicom_to_raw(dicom_file, args.raw_path)
            print_matching_files(matches)

        else:  # both files
            print_comparison(args.dicom_path, args.raw_path)

    elif args.dicom_path:  # only dicom
        print_dicom_metadata(args.dicom_path)

    elif args.raw_path:  # only raw
        print_raw_metadata(args.raw_path)

    else:  # no paths given
        parser.print_help()
