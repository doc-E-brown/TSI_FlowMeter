#! /usr/bin/env python
"""
This file is used to store a repository of commonly used tools
"""
__author__ = "Ben Johnston"
__revision__ = "0.1"
__date__ = "04/09/2014"
__license__ = "GPL"

##IMPORTS#####################################################################
from datetime import datetime
import os
import csv
##############################################################################


class logger(object):
    """!
    A generic data logging class. This class is capable of generating
    info logs, error logs and adding data to within csv and other file types.
    Extend this class to incorporate additional logging functionality.
    """
    def __init__(self, file_name='info.log', debug_level=0):
        """!
        A constructor for the class
        @param self The pointer for the object
        @param file_name The file name for the log file.
        @param debug_level Controls debugging functionality for the class.
        Set to 1 to print the entered message to the command line only.
        Set to 2 to print the entered message to the command line and
        to log the message to a file.
        """
        ##@var debug_level
        #Controls the debug functionality of the class
        self.debug_level = debug_level
        ##@var file_name
        #Contains the file name for the log
        self.file_name = file_name

    def info(self, msg, date_time_flag=True):
        """!
        This method prints the msg to the screen or file as a string
        based upon <i>debug_level</i>
        @param msg A string containing the message to be logged.
        @param date_time_flag A flag which is set to true to append a date
        and time stamp to the front of the message prior to logging.
        """
        if date_time_flag:
            #Now in a string format
            now = datetime.strftime(datetime.now(), '%d/%m/%Y %H:%M:%S - ')
            #New log message
            log_message = now + msg
        else:
            log_message = msg
        #Print the message to the command line prompt if the debug level is
        #above the required level
        if self.debug_level >= 1:
            print log_message
        #Write the message to file if the debug level is above the required
        #level
        if self.debug_level >= 2:
            with open(self.file_name, 'a') as f:
                f.write(log_message + "\n")


class csvLogger(object):
    """!
    A class used to log csv files.  This class is extended from the logger
    class.
    """
    def __init__(self, file_name='info.csv', header=['Date', 'Time'],
                 debug_level=0):
        """!
        A constructor for the class
        @param self The pointer for the object
        @param file_name The file name for the log file
        @param header The first row of data to be written to a new file.  This
        row is generally used as a header.
        @param debug_level Controls debugging functionality for the class.
        Set to 1 to print the entered message to the command line only.
        Set to 2 to print the entered message to the command line and to
        log the message to a file.
        """
        ##@var file_name
        #The name of the log file
        self.file_name = file_name
        ##@var debug_level
        #Controls the debug functionality of the class
        self.debug_level = debug_level
        ##Assign the header information
        ##@var header
        #Capture the header information for the csv
        self.header = header
        #If the file does not exist already write the header information as the
        #first line
        if not os.path.isfile(self.file_name):
            self.write_line(self.header)

    def write_line(self, message, date_time_flag=False):
        """!
        Write a line of data to the csv file
        @param self The pointer for th object
        @param message A list of data to write to the csv file where each
        element within the list will correspond with an entry within the file
        separated by commas
        @param date_time_flag A flag which is set to true to append a date
        and time stamp to the front of the message prior to logging.
        """
        if type(message) is not list:
            formatted_msg = message.split(',')
        else:
            formatted_msg = message
        if date_time_flag:
            #Now in a string format
            now_date = datetime.strftime(datetime.now(), '%d/%m/%Y')
            now_time = datetime.strftime(datetime.now(), '%H:%M:%S')
            formatted_msg.insert(0, now_time)
            formatted_msg.insert(0, now_date)
        with open(self.file_name, 'a') as f:
            writer = csv.writer(f,
                                #quotechar=' ',
                                #quoting=csv.QUOTE_NONE,
                                )
            if self.debug_level >= 1:
                print formatted_msg
            writer.writerow(formatted_msg)
