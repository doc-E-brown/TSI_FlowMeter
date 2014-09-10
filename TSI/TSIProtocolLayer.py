#! /usr/bin/env python
"""
Python module for operation of a TSI Flow Meter
"""
__author__ = "Ben Johnston"
__revision__ = "0.1"
__date__ = "Wed Sep 10 10:26:45 EST 2014"
__copyright__ = "GPL License"

##IMPORTS#####################################################################
import serial
from TSILogger import logger
import os
from glob import glob
##############################################################################


class TSIException(Exception):
    """!
    Class to handle exceptions within the TSI module
    """
    def __init__(self, msg=None):
        """!
        The constructor for the class.
        @param self The pointer for the object
        @param msg The message to be displayed within the exception
        """
        Exception.__init__(self, msg)
        ##@var msg
        #The message to report for the exception
        self.msg = msg

    def __str__(self):
        """!
        This method provides a string representation of the exception
        @param self The pointer for the object
        @return A string representation of the exceptions
        """
        return self.msg


class TSIProtocolLayer(object):

    def __init__(self, serial_port=None, debug_level=0):
        """!
        The constructor for the class
        @param serial_port
        @param log_data
        """
        #Create a results logger for the object
        self.debug_level = debug_level
        self.info_logger = logger(debug_level=self.debug_level)
        #Initialise the module
        #Set the communications parameters of the device
        self.baudrate = 38400
        self.bytesize = serial.EIGHTBITS
        self.xonxoff = False
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 0.5
        self.rtscts = False
        self.dsrdtr = False
        #Create the serial object for the device
        self.device = serial.Serial(baudrate=self.baudrate,
                                    bytesize=self.bytesize,
                                    parity=self.parity,
                                    stopbits=self.stopbits,
                                    timeout=self.timeout,
                                    writeTimeout=self.timeout,
                                    xonxoff=self.xonxoff,
                                    rtscts=self.rtscts,
                                    dsrdtr=self.dsrdtr)
        if serial_port is None:
            if os.name is 'nt':
                range_of_ports = []
                for i in range(256):
                    range_of_ports.append('COM%d' % i)
            elif os.name is 'posix':
                range_of_ports = glob('/dev/ttyS*') + glob('/dev/ttyUSB*')
            #If the port is not specified, find it
            for i in range_of_ports:
                #Try and open the port
                try:
                    self.device.port = i
                    self.info_logger.info(self.device.port)
                    self.device.close()
                    self.device.open()
                    self.send_msg('?')
                    if self.read_msg() == 'OK':
                        self.port = self.device.port
                        return
                    self.device.close()
                except:
                    self.device.port = None
        else:
            self.device.port = serial_port
            self.port = self.device.port
            self.device.open()

    def send_msg(self, message):
        """!
        Send a message to the TCI device
        @param self The pointer for the object
        @param message The message to send to the TSI device
        """
        try:
            self.device.write('%s\r' % message)
            self.info_logger.info('To TSI@%s: %s' %
                                  (self.device.port, message))
        except:
            raise TSIException('Unable to write to TSI')

    def read_msg(self):
        """!
        Read a message from the TCI device
        @param self The pointer for the object
        """
        try:
            response = self.device.readline()
            if response != '':
                response = response.strip('\r\n').strip(' ')
            self.info_logger.info('From TSI@%s: %s' %
                                  (self.device.port, response))
            return response
        except:
            raise TSIException('Unable to read from TSI')
