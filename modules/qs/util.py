#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
"""Utility functions for inclusion in public QS package API.

Includes lots of little functions that wouldn't be worth writing normally
but end up being super useful over multiple scripts.

The requirements for functionsto be in this module:
    - Simple, intuitive
    - Useful among multiple scripts/modules
"""

import os
import re
import json
import string
import random
import textwrap
import subprocess
import inspect
import sys


def dumps(arbitry_obj, sort=True):
    """Dumps like json.dumps. Note that by default, list order is not
    maintained.
    """
    if sort is True and type(arbitry_obj) is list:
        arbitry_obj = sorted(arbitry_obj)
    return json.dumps(arbitry_obj, indent=4, sort_keys=sort)


def pp(arbitry_obj):  # pragma: no cover
    """Like pprint.pprint"""
    print_break('-')
    print dumps(arbitry_obj) if arbitry_obj else str(arbitry_obj)
    print_break('-')


def print_break(break_str='*'):  # pragma: no cover
    """Print a break that's the width of the terminal for grouping output info.

    Args:
        break_str: the string to use in the break on repeat.
    """
    columns = float(subprocess.check_output(['stty', 'size']).split()[1])
    print
    print break_str * int(columns / len(break_str))
    print


def ask(message, width=70):
    """Like w_print, but returns a valu based on the user typing"""
    wrapper = textwrap.TextWrapper()
    wrapper.width = width
    return raw_input('\n' + wrapper.fill(message) + '\n').strip()


def dict_list_to_dict(dict_list, id_key='id'):
    """Takes a list of dicts and flattens them to a single dict using the
    id_key for the keys in the flattened dict.
    """
    return {i[id_key]: i for i in dict_list}


def dict_to_dict_list(large_dict):
    """Takes a single dict and expands it out to a list of dicts."""
    return [v for k, v in large_dict.iteritems()]


def rand_str(size=6, chars=string.letters + string.digits):
    """http://stackoverflow.com/a/2257449/1628796"""
    return ''.join(random.choice(chars) for _ in range(size))


def merge(*args):
    """Returned merged version of indefinite number of dicts. Just like the
    builtin dict() method, args to right get precedent over args to the left.

    Example usage: qs.merge({1: 2}, {3: 4}).
    """
    merged = []
    for unmerged in args:
        for item in unmerged.items():
            merged.append(item)
    return dict(merged)


def running_from_test():
    """Tell whether the current script is being run from a test"""
    return 'nosetests' in sys.argv[0]


def clean_id(some_id, func_name=None):
    """Clean some_id to be used as a QS-generated id somewhere. Either returns
    a cleaned string (not int or unicode, etc), or throws an error.

    Args:
        func_name: the name of the function this is being called from/for,
            to be used in exception messages. Mainly there for clean_args()
    """
    if is_valid_id(some_id, func_name) is True:
        return str(some_id)


def is_valid_id(some_id, check_only=False, func_name=None):
    """Check if some_id is a valid id. If check_only is True, then no errors
    are thrown, just a silent check.
    """
    id_part = 'id {}'.format(some_id)
    try:
        if func_name:
            id_part += " for function '{}'".format(func_name)
        if not some_id and some_id != 0:
            raise ValueError('The {} must not be none'.format(id_part))
        elif type(some_id) is int or str(some_id) == some_id:
            return True
        else:
            raise TypeError('The {} must be a string or int'.format(id_part))
    except:
        if check_only:
            return False
        else:
            raise


def is_builtin(obj):
    """Determine if obj is a builtin, like a string or int"""
    builtins = [int, str, dict, list, set, float]
    return type(obj) in builtins


def make_id(*args):
    """Make an id based on arbitrary number of args. This id is in the format
    of: 'arg1:arg2:...:argn'. This is useful for when multiple values must
    be used to make a key unique.
    """
    if not all(str(i) == i or type(i) is int for i in args):
        raise TypeError(
            'All args in make_id must be string or ints. Actual values: '
            '{}'.format(args))
    return ':'.join(str(i) for i in args)


def sets_to_lists(list_of_dicts):
    """Convert all sets in the values in a list of dicts to lists. This is good
    when list_of_dicts will be JSON-serialized, since JSON doesn't take sets.
    """
    for original_dict in list_of_dicts:
        for key, val in original_dict.iteritems():
            if type(val) is set:
                original_dict[key] = list(val)


def format_phone(raw_phone):
    """Format a phone number, such as '1234567890' --> '(123) 456-7890'"""
    if not valid_us_phone(raw_phone): return raw_phone
    return '(%s%s%s) %s%s%s-%s%s%s%s' % tuple(digits(raw_phone))


def valid_us_phone(raw_phone):
    """Tell whether a phone number is a valid US phone number"""
    return raw_phone and len(digits(raw_phone)) == 10


def digits(string):
    """Return just the digits from string"""
    return ''.join([i for i in string if i.isdigit()])


def finance_to_float(finance):
    """Convert a finance number, such as '$100.07' to a float"""
    return float(''.join([i for i in finance if i in '-.0123456789']))


def find_dups_in_dict_list(dict_list, key):
    """Find all the duplicates in a list of dicts by a certain key. Only the
    value for the key has to match for two dicts to be consdered a duplicate,
    not the entire dict. Returns a list of the duplicate entries.
    """
    by_key = {i[key]: [] for i in dict_list}
    for record in dict_list:
        by_key[record[key]].append(record)
    duplicates = [v for k, v in by_key.iteritems() if len(v) > 1]
    return sum(duplicates, [])


def to_bool(string):
    """Convert string to bool. Not case-sensitive.
    Equates to True:
        y, yes, t, true, (any number except 0)
    Equates to False:
        n, no, f, false, 0

    If string is in neither of these, ValueError is raised
    """
    string = str(string).strip().lower()
    try:
        return bool(float(string))
    except ValueError:
        pass

    if string in ['y', 'yes', 't', 'true']:
        return True
    elif string in ['n', 'no', 'f', 'false']:
        return False
    else:
        raise ValueError


def w_print(message, width=70):
    """Wrapped print - wrapped to width chars per line"""
    wrapper = textwrap.TextWrapper()
    wrapper.width = width
    print wrapper.fill(message) + '\n'


def validate_xml(file_path):
    """
    Validates the XML file at file_path and returns the file object

    Validates to check that the XML is actually an XML doc. If the file isn't
    valid XML, then the script fails; any future use of the contents/file can
    assume that the XML is valid.

    Also adds the version tag to the start of the file if it's not there
    already. This ensures that the XML is completely valid.

    Args:
        file_path: the path to the file

    Returns:
        the file contents as a valid XML string
    """
    xml = open(file_path, 'r+')
    contents = xml.read()
    xml.seek(0)
    if not contents.startswith('<'):
        raise ValueError(messages.invalid_file)
    if '<?xml version=' not in contents:
        contents = '<?xml version="1.0"?>\n\n' + contents
        xml.write(contents)
        xml.seek(0)
    return xml


def hex_to_dec(hex_val):
    """Convert a hex value to a decimal"""
    modified_hex_val = str(hex_val)
    modified_hex_val = modified_hex_val.strip().lstrip('#')
    modified_hex_val = '0x' + modified_hex_val
    try:
        return int(modified_hex_val, 0)
    except ValueError:
        raise ValueError("{} isn't a valid hex value.".format(hex_val))


def unique_path(original_file_path, suffix='', use_random=False,
        extension=None):
    """Make a unique file path based on the provided original file path.

    Defaults to adding an increasing integer at the end of the file name, such
    as text.txt => text(0).txt, then text(0).txt => text(1).txt.

    Suffix would add a specific suffix to reflect the fact the file has
    changed, such as text.txt => text_changed.txt, then
    text_changed.txt => text_changed(0).txt

    If use_random is True, then a 3 digit random number is appended to the file
    name, like so: text.txt => text594.txt, then text594.txt => text221.txt.

    If random is true and suffix is defined, it'll be text_changed123.txt

    Args:
        original_file_path: the path of the original file to be similar to, but
            not overwrite
        suffix: suffix to add to file, such as '_changed'
        use_random: append a random number to the file name if True
        extension: supply a new extension instead of the existing one on
            original_file_path.
    """
    base_path, filename_with_extension = os.path.split(original_file_path)
    filename, original_extension = os.path.splitext(filename_with_extension)

    if use_random is True:
        before_number = filename[:-3]
        last_three = filename[-3:]
        if not all(i.isdigit() for i in last_three):
            before_number += last_three
        random_digits = str(random.randint(100, 999))
        new_filename = '{}{}{}'.format(before_number, suffix, random_digits)
    else:
        match = re.match(r'(.+)\((\d+)\)$', filename)
        if match:
            before_number = match.group(1)
            number = int(match.group(2)) + 1
        else:
            before_number = filename
            number = 0
        new_filename = '{}{}({})'.format(before_number, suffix, number)

    new_extension = (extension or original_extension).lstrip('.')
    return '{}/{}.{}'.format(base_path, new_filename, new_extension)

# ==============
# = Decorators =
# ==============


def clean_arg(func):
    """Clean the first argument of the decorated function. Useful if an ID is
    passed as the first arg.
    """

    def inner(*args, **kwargs):
        args = list(args)
        index = 0 if is_builtin(args[0]) else 1
        args[index] = clean_id(args[index])
        return func(*args, **kwargs)
    return inner

# TODO: implement clean_args for multiple args
