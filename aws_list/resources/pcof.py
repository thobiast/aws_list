"""
Python Collection Of Functions

This module has a collection of many small generic useful functions.

Developed for Python 3
"""

# Author: Thobias Salazar Trevisan
# Site: http://thobias.org

import logging
import subprocess
import datetime
import sys
import re
import smtplib
import collections
import prettytable


##############################################################################
##############################################################################
## Print text
##############################################################################
##############################################################################

def msg(color,
        msg_text,
        exitcode=0,
        *,
        mail_from=None,
        mail_to=None,
        mail_server='localhost',
        subject=None,
        end='\n'):
    """
    Print colored text.

    Arguments:
        size      (str): color name (blue, red, green, yellow,
                                     cyan or nocolor)
        msg_text  (str): text to be printed
        exitcode  (int, opt): Optional parameter. If exitcode is different
                              from zero, it terminates the script, i.e,
                              it calls sys.exit with the exitcode informed

    Keyword arguments to send the msg_text by email too:
        mail_from   (str, opt): send email from this address
        mail_to     (str, opt): send email to this address
        subject     (str, opt): mail subject
        mail_server (str, opt): mail server address
        end         (str):      string appended after the last value,
                                default a newline

    Exemplo:
        msg("blue", "nice text in blue")
        msg("red", "Error in my script.. terminating", 1)
    """

    color_dic = {'blue': '\033[0;34m',
                 'red': '\033[1;31m',
                 'green': '\033[0;32m',
                 'yellow': '\033[0;33m',
                 'cyan': '\033[0;36m',
                 'resetcolor': '\033[0m'}

    if not color or color == 'nocolor':
        print(msg_text)
    else:
        try:
            print(color_dic[color] + msg_text + color_dic['resetcolor'],
                  end=end)
        except KeyError as exc:
            raise ValueError("Invalid color") from exc

    # Send email if necessary
    if mail_from and mail_to and subject:
        send_email(mail_from, mail_to, subject, msg_text, mail_server)

    # flush stdout
    sys.stdout.flush()

    if exitcode:
        sys.exit(exitcode)


def print_table(header, rows, *, sortby='', alignl='', alignr='', hrules=''):
    """
    Print table
    Arguments:
        header     (list): List with table header
        rows       (list): Nested list with table rows
                           [ [row1], [row2], [row3], ... ]

    Keyword arguments (optional):
        sortby      (str): header name to sort the output
        alignl     (list): headers name to align to left
        alignr     (list): headers name to align to right
        hrules      (str): Controls printing of horizontal rules after rows.
                           Allowed values: FRAME, HEADER, ALL, NONE
    """
    output = prettytable.PrettyTable(header)
    output.format = True
    if hrules:
        output.hrules = getattr(prettytable, hrules)

    for row in rows:
        row_entry = list()
        for pos in row:
            row_entry.append(pos)
        output.add_row(row_entry)

    if sortby:
        # if sortby is invalid, ie, does not exist on header,
        # sort by first column by default
        output.sortby = sortby if sortby in header else header[0]
    for left in alignl:
        output.align[left] = 'l'
    for right in alignr:
        output.align[right] = 'r'

    print(output)


##############################################################################
##############################################################################
## Email
##############################################################################
##############################################################################

def send_email(mail_from, mail_to, subject, body, mailserver='localhost'):
    """
    Send an email using smtplib module

    Arguments:
        mail_from   (str): send email from this address
        mail_to     (str): send email to this address
        subject     (str): mail subject
        mail_server (str, opt): mail server address. Default is localhost
    """
    mail_msg = """\
From: %s
To: %s
Subject: %s

%s
""" % (mail_from, mail_to, subject, body)

    # send the email
    try:
        smtpobj = smtplib.SMTP(mailserver)
        smtpobj.sendmail(mail_from, mail_to, mail_msg)
    finally:
        smtpobj.quit()


##############################################################################
##############################################################################
## Log
##############################################################################
def setup_logging(logfile=None, *,
                  filemode='a', date_format=None, log_level='DEBUG'):
    """
    Configure logging

    Arguments (opt):
        logfile     (str): log file to write the log messages
                               If not specified, it shows log messages
                               on screen (stderr)
    Keyword arguments (opt):
        filemode    (a/w): a - log messages are appended to the file (default)
                           w - log messages overwrite the file
        date_format (str): date format in strftime format
                           default is %m/%d/%Y %H:%M:%S
        log_level   (str): specifies the lowest-severity log message
                           DEBUG, INFO, WARNING, ERROR or CRITICAL
                           default is DEBUG
    """
    dict_level = {'DEBUG': logging.DEBUG,
                  'INFO': logging.INFO,
                  'WARNING': logging.WARNING,
                  'ERROR': logging.ERROR,
                  'CRITICAL': logging.CRITICAL}

    if log_level not in dict_level:
        raise ValueError("Invalid log_level")
    if filemode not in ['a', 'w']:
        raise ValueError("Invalid filemode")

    if not date_format:
        date_format = '%m/%d/%Y %H:%M:%S'

    log_fmt = '%(asctime)s %(module)s %(funcName)s %(levelname)s %(message)s'

    try:
        logging.basicConfig(level=dict_level[log_level],
                            format=log_fmt,
                            datefmt=date_format,
                            filemode=filemode,
                            filename=logfile)
    except:
        raise

    return logging.getLogger(__name__)


##############################################################################
##############################################################################
## Dictionary
##############################################################################
##############################################################################

def nested_dict():
    """
    Returns a nested dictionary, i.e, an dictionary with
    arbitrary number of levels.

    Example:
    >>> mydict = nested_dict()
    >>> mydict['aa']['bb']['cc'] = 'teste'
    >>> print(mydict)
         defaultdict(<function nested_dict at 0x7f1e74b8bea0>, {'aa':
         defaultdict(<function nested_dict at 0x7f1e74b8bea0>, {'bb':
         defaultdict(<function nested_dict at 0x7f1e74b8bea0>, {'cc':
         'teste'})})})
    >>> import pprint
    >>> pprint.pprint(mydict)
         {'aa': {'bb': {'cc': 'teste'}}}

    """
    return collections.defaultdict(nested_dict)


def find_key(dict_obj, key):
    """
    Function to search in a dictionary and search for an specific key
    It supports nested dictionary
    Params:
        dict_obj    (obj): A list or a dictionary
        key         (str): dictionary key

    Return a list with values that matches the key
    """
    # List to store values
    results = list()

    # if dict_obj is a dictionary
    if isinstance(dict_obj, dict):
        for k, v in dict_obj.items():
            # if value is == key
            if k == key:
                results.append(v)
            else:
                # call function again, it can be a nested dict
                results.extend(find_key(v, key))
    # If dict_obj is a list
    elif isinstance(dict_obj, list):
        # for each item, call again the function, as maybe there are
        # dict inside the list
        for item in dict_obj:
            results.extend(find_key(item, key))

    return results


##############################################################################
##############################################################################
## Execute command
##############################################################################
##############################################################################

def run_cmd(cmd):
    """
    Execute a command on the operating system

    Arguments:
        cmd    (str): the command to be executed

    Return:
        - If command complete with return code zero
        return: command_return_code, stdout

        - If command completes with return code different from zero
        return: command_return_code, stderr
    """
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)

    # Poll process for new output until finished
    stdout_output = ""
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() is not None:
            break
        # print lines to stdout
        #sys.stdout.write(nextline)
        #sys.stdout.flush()
        stdout_output += nextline

    stderr = process.communicate()[1]

    if process.returncode:
        return process.returncode, stderr
    else:
        return process.returncode, stdout_output


##############################################################################
##############################################################################
## Validate IP address
##############################################################################
##############################################################################
def validate_ip(ip_address):
    """
    Validate IP address format

    Arguments:
        ip_address   (str): IP address
    """
    log.debug("params: ip_address: %s", ip_address)

    ip_regex = r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(/[0-9]{1,3})?$'
    regex = re.compile(ip_regex)
    return regex.match(ip_address)


##############################################################################
##############################################################################
## Bytes convertion
##############################################################################
##############################################################################

def bytes2human(size, *, unit='', precision=2, base=1024):
    """
    Convert number in bytes to human format

    Arguments:
        size        (int): bytes to be converted

    Keyword arguments (opt):
        unit       (str): If it will convert bytes to a specific unit
                          'KB', 'MB', 'GB', 'TB', 'PB', 'EB'
        precision  (int): number of digits after the decimal point
        base       (int): 1000 - for decimal base
                          1024 - for binary base (it is the default)

    Returns:
        (int): number
        (str): unit (Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']

    Exemple:
        >>> bytes2human(10)
        ('10.00', 'Bytes')
        >>> bytes2human(2048)
        ('2.00', 'KB')
        >>> bytes2human(27273042329)
        ('25.40', 'GB')
        >>> bytes2human(27273042329, precision=1)
        ('25.4', 'GB')
        >>> bytes2human(27273042329, unit='MB')
        ('26009.60', 'MB')
    """
    # validate parameters
    if not isinstance(precision, int):
        raise ValueError("precision is not a number")
    if not isinstance(base, int):
        raise ValueError("base is not a number")
    try:
        num = float(size)
    except ValueError:
        raise ValueError("Value is not a number")

    suffix = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']

    # If it needs to convert bytes to a specific unit
    if unit:
        try:
            num = num / base ** suffix.index(unit)
        except ValueError:
            raise ValueError("Error: unit must be KB, MB, GB, TB, PB or EB")
        return "{0:.{prec}f}".format(num, prec=precision), unit

    # Calculate the greatest unit for the that size
    for counter, suffix_unit in enumerate(suffix):
        if num < base:
            return "{0:.{prec}f}".format(num, prec=precision), suffix_unit
        if counter == len(suffix)-1:
            raise ValueError("Value greater than the highest unit")
        num /= base


def human2bytes(size, unit, *, precision=2, base=1024):
    """
    Convert size from human to bytes

    Arguments:
        size       (int): number
        unit       (str): converts from this unit to bytes
                          'KB', 'MB', 'GB', 'TB', 'PB', 'EB'

    Keyword arguments (opt):
        precision  (int): number of digits after the decimal point
                          default is 2
        base       (int): 1000 - for decimal base
                          1024 - for binary base (it is the default)

    Returns:
        (int) number in bytes

    Example:
        >>> human2bytes(10, 'GB')
        '10737418240.00'
        >>> human2bytes(10, 'GB', precision=0)
        '10737418240'
        >>> human2bytes(10, 'PB')
        '11258999068426240.00'

    """
    dic_power = {'KB': base,
                 'MB': base ** 2,
                 'GB': base ** 3,
                 'TB': base ** 4,
                 'PB': base ** 5,
                 'EB': base ** 6}
    if unit not in dic_power:
        raise ValueError("Invalid unit. It must be KB, MB, GB, TB, PB or EB")

    try:
        num_bytes = float(size) * int(dic_power[unit])
    except ValueError:
        raise ValueError("Value is not a number")

    return "{0:.{prec}f}".format(num_bytes, prec=precision)


##############################################################################
##############################################################################
## Percentage Calculator
##############################################################################
##############################################################################

def pct_two_numbers(number1, number2, *, precision='2'):
    """
    Calculate the percentage of number1 to number2, i.e,
    number1 is what percent of number2

    Arguments:
        number1 (int): number
        number2 (int): number

    Keyword arguments (opt):
        precision  (int): number of digits after the decimal point
                          default is 2

    Returns:
        (int): Pct value

    Example:
    >>> pct_two_numbers(30, 90)
    '33.33'
    >>> pct_two_numbers(30, 90, precision=0)
    '33'
    >>> pct_two_numbers(30, 90, precision=4)
    '33.3333'
    >>> pct_two_numbers(10, 50)
    '20.00'
    """
    try:
        num_pct = number1 * 100 / number2
        return "{0:.{prec}f}".format(num_pct, prec=precision)
    except ZeroDivisionError:
        return "{0:.{prec}f}".format(0, prec=precision)


def x_pct_of_number(pct, number, *, precision='2'):
    """
    Calculate what is the x% of a number

    Arguments:
        pct        (int): percentage
        number     (int): number

    Keyword arguments (opt):
        precision  (int): number of digits after the decimal point
                          default is 2

    Returns:
        (int):  number

    Exemple:
    >>> x_pct_of_number(33.333, 90)     # what is 33.333% of 90
    '30.00'
    >>> x_pct_of_number(40, 200)        # what is 40% of 200
    '80.00'
    >>> x_pct_of_number(40.9, 200)      # what is 40.9* of 200
    '81.80'
    >>> x_pct_of_number(40.9, 200, precision=4)
    '81.8000'
    >>> x_pct_of_number(40.9, 200, precision=0)
    """
    num = number * pct / 100
    return "{0:.{prec}f}".format(num, prec=precision)


##############################################################################
##############################################################################
## Unix epoch time conversion
##############################################################################
##############################################################################

def epoch_time_to_human(epoch, *, date_format='%c', utc='no'):
    """
    Convert a unix epoch time to human format

    Unix epoch time -  number of seconds that have elapsed since
                       00:00:00 Coordinated Universal Time (UTC),
                       1 January 1970

    Arguments:
        epoch       (int):    unix epoch time (timestamp)

    Keyword arguments (opt):
        date_format (str):    strftime format to show the epoch time
                              default is '%c' (Locale’s appropriate
                              date and time representation)
        utc         (yes/no): If unix epoch time in UTC timezone
                              default is no

    Example:
    >>> epoch_time_to_human(1530324373,'%m/%d/%Y %H:%M:%S')
    '06/29/2018 23:06:13'
    >>> epoch_time_to_human(1530324373)
    'Fri Jun 29 23:06:13 2018'
    >>> epoch_time_to_human(1530324373, utc='yes')
    'Sat Jun 30 02:06:13 2018'
    """
    if utc == 'yes':
        return datetime.datetime.utcfromtimestamp(epoch).strftime(date_format)
    else:
        return datetime.datetime.fromtimestamp(epoch).strftime(date_format)


def epoch_time_now(*, utc='no'):
    """
    Return current date and time in unix epoch time format

    Unix epoch time -  number of seconds that have elapsed since
                       00:00:00 Coordinated Universal Time (UTC),
                       1 January 1970

    Arguments:
        utc         (yes/no): If returns unix epoch time in UTC timezone
                              default is no
    Example:
    >>> epoch_time_now()
    1530325275
    """
    if utc == 'yes':
        return int(datetime.datetime.utcnow().timestamp())
    elif utc == 'no':
        return int(datetime.datetime.now().timestamp())
    else:
        raise TypeError("error: epoch_time_now: utc is invalid")


def epoch_time_min_ago(minutes=5, *, utc='no'):
    """
    Return current date and time less x minutes in unix epoch time format

    Unix epoch time -  number of seconds that have elapsed since
                       00:00:00 Coordinated Universal Time (UTC),
                       1 January 1970

    Arguments (opt):
        minutes  (int): Number of minutes ago to return unix timestamp
                        default is 5 minutes

    Keyword arguments (opt):
        utc         (yes/no): If unix epoch time in UTC timezone
                              default is no
    Example:
    >>> epoch_time_min_ago()
    1530325377
    >>> epoch_time_min_ago(30)
    1530323879
    """
    return int(epoch_time_now(utc=utc) - (60 * minutes))


def epoch_time_hours_ago(hours=1, *, utc='no'):
    """
    Return current date and time with less x hours in unix epoch time format

    Unix epoch time -  number of seconds that have elapsed since
                       00:00:00 Coordinated Universal Time (UTC),
                       1 January 1970

    Arguments (opt):
        hours     (int):    Number of hours ago to return unix timestamp
                            default is 1 hour

    Keyword arguments (opt):
        utc       (yes/no): If unix epoch time in UTC timezone
                            default is no
    Example:
    >>> epoch_time_hours_ago()
    1530322279
    >>> epoch_time_hours_ago(8)
    1530297083
    """
    return int(epoch_time_now(utc=utc) - (hours * 3600))


def epoch_time_days_ago(days=1, *, utc='no'):
    """
    Return current date and time with less x days in unix epoch time format

    Unix epoch time -  number of seconds that have elapsed since
                       00:00:00 Coordinated Universal Time (UTC),
                       1 January 1970

    Arguments (opt):
        days       (int):   Number of days ago to return unix timestamp
                              default is 1 day

    Keyword arguments (opt):
        utc       (yes/no): If unix epoch time in UTC timezone
                            default is no
    Example:
    >>> epoch_time_days_ago()
    1530239517
    >>> epoch_time_days_ago(7)
    1529721118
    """
    return int(epoch_time_now(utc=utc) - (days * 24 * 3600))


# vim: ts=4
