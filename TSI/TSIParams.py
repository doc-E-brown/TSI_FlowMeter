#! /usr/bin/env python
"""
Python module for operation of a TSI Flow Meter
"""
__author__ = "Ben Johnston"
__revision__ = "0.1"
__date__ = ""
__copyright__ = "GPL License"

##IMPORTS#####################################################################
from TSIProtocolLayer import TSIProtocolLayer
##############################################################################


#Define an exception class
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


class TSIParams(TSIProtocolLayer):

    #Define class wide variables
    #Units variables
    STD_FLOW_RATE = 'S'
    VOL_FLOW_RATE = 'V'

    #Measurement variables
    FLOW = 'F'
    PRESSURE = 'P'

    def __init__(self, serial_port=None, debug_level=0):
        """!
        The constructor for the class
        @param serial_port
        @param log_data
        """
        #Initialise the super class
        TSIProtocolLayer.__init__(self,
                                  serial_port,
                                  debug_level)

    def set_sample_rate(self, rate=500):
        """!
        This method sets the sample rate used by data measurements
        self.measure_FTP and self.measure_volume.  Once the sample rate has
        been set, self.sample_rate will then be available containing the
        current sample rate used by the device.
        @param self The pointer for the object
        @param rate The rate at which measurements are taken specified in
        milliseconds per sample.  The allowable rates are 1 to 1000.  Those
        sample rates which lie outside this range will be capped at the
        closes limit.
        """
        #Check the sample number has been entered correctly
        if rate <= 1:
            signed_rate = 1
        elif rate >= 1000:
            signed_rate = 1000
        else:
            signed_rate = rate
        sample_str_len = len(str(int(signed_rate)))
        if (sample_str_len < 4):
            adjusted_rate = '0' * (4 - sample_str_len) + \
                            '%d' % signed_rate
        else:
            adjusted_rate = str(signed_rate)
        #The message to send the device is constructed from:
        #1. SSR to denote setting the sample rate
        #2. The formatted sample rate as per above
        self.send_msg('SSR%s' % adjusted_rate)
        acknowledge = self.read_msg()
        if acknowledge == 'OK':
            self.sample_rate = int(adjusted_rate)
            return
        else:
            #An error occurred
            if acknowledge.find('ERR') > 0:
                error = acknowledge.strip('ERR')
                err_msg = 'Error %d returned requesting measurement' %\
                          error
            else:
                err_msg = 'Unknown response received: %s' % err_msg
            raise TSIException(err_msg)

    def set_units(self, flow_rate_type=STD_FLOW_RATE):
        """!
        This method is used to configure the units of flow for data displayed
        on the LCD and received through serial communications.  Please note
        that either std_flow_rate must be set, if both or none are set
        std_flow_rate will be assumed.
        @param self The pointer for the object
        @param std_flow_rate Set to True to use standard flow rate units
        (l/min)
        @param vol_flow_rate Set the True to use volumetric flow rate units
        are used
        """
        #Prefix for communications message
        #According to the communications manual
        #SU denotes set the flow units
        #Send the message
        self.send_msg('SU%s' % flow_rate_type)
        acknowledge = self.read_msg()
        if acknowledge == 'OK':
            #The setting was correctly applied
            return
        else:
            #An error occurred
            if acknowledge.find('ERR') > 0:
                error = acknowledge.strip('ERR')
                err_msg = 'Error %d returned requesting measurement' %\
                          error
            else:
                err_msg = 'Unknown response received: %s' % acknowledge
            raise TSIException(err_msg)

    def get_serial_no(self):
        """!
        This method returns the serial number of the device
        @param self The point for the object
        @return The serial number of the device
        """
        #The command SN retrieves the serial number for the device
        self.send_msg('SN')
        acknowledge = self.read_msg()
        if acknowledge == 'OK':
            #The command was successfully received
            return self.read_msg().strip(' ')
        else:
            #An error occurred
            if acknowledge.find('ERR') > 0:
                error = acknowledge.strip('ERR')
                err_msg = 'Error %d returned requesting serial number' %\
                          error
            else:
                err_msg = 'Unknown response received: %s' % err_msg
            raise TSIException(err_msg)

    def get_cal_date(self):
        """!
        This method returns the current date of calibration of the device
        @param self The pointer for the object
        @return The date of previous calibration as a string in the format
        'month/day/year'
        """
        #The command DATE retrieves the last calibration date for the device
        self.send_msg('DATE')
        acknowledge = self.read_msg()
        if acknowledge == 'OK':
            #The command was successfully received
            return self.read_msg().strip(' ')
        else:
            #An error occurred
            if acknowledge.find('ERR') > 0:
                error = acknowledge.strip('ERR')
                err_msg = 'Error %d returned requesting calibration date' %\
                          error
            else:
                err_msg = 'Unknown response received: %s' % err_msg
            raise TSIException(err_msg)

    def get_model_no(self):
        """!
        This method returns the model number of the device
        @param self The pointer for the object
        @return The model number of the object
        """
        #The command MN retrieves the model number for the device
        self.send_msg('MN')
        acknowledge = self.read_msg()
        if acknowledge == 'OK':
            #The command was successfully received
            return self.read_msg().strip(' ')
        else:
            #An error occurred
            if acknowledge.find('ERR') > 0:
                error = acknowledge.strip('ERR')
                err_msg = 'Error %d returned requesting the model number' %\
                          error
            else:
                err_msg = 'Unknown response received: %s' % err_msg
            raise TSIException(err_msg)

    def get_firmware_rev(self):
        """!
        This method returns the model number of the device
        @param self The pointer for the object
        @return The model number of the object
        """
        #The command REV retrieves the firmware revision for the device
        self.send_msg('REV')
        acknowledge = self.read_msg()
        if acknowledge == 'OK':
            #The command was successfully received
            return self.read_msg().strip(' ')
        else:
            #An error occurred
            if acknowledge.find('ERR') > 0:
                error = acknowledge.strip('ERR')
                err_msg = 'Error %d returned requesting the firmware revision' %\
                          error
            else:
                err_msg = 'Unknown response received: %s' % err_msg
            raise TSIException(err_msg)
