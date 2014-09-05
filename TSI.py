#! /usr/bin/env python
"""
Python module for operation of a TSI Flow Meter
"""
__author__ = "Ben Johnston"
__revision__ = "0.1"
__date__ = ""
__copyright__ = "GPL License"

##IMPORTS#####################################################################
import serial
from logging import csvLogger, logger
from datetime import datetime
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


class TSI(object):

    #Define class wide variables
    #Units variables
    STD_FLOW_RATE = 'S'
    VOL_FLOW_RATE = 'V'

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
        self.port = serial_port
        self.baudrate = 38400
        self.bytesize = serial.EIGHTBITS
        self.xonxoff = False
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 2
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
        if self.port is None:
            #If the port is not specified, find it
            for i in range(10):
                #Try and open the port
                try:
                    self.device.port = 'COM%d' % i
                    self.info_logger.info(self.device.port)
                    self.device.close()
                    self.device.open()
                    self.send_msg('?')
                    if self.read_msg() == 'OK':
                        self.port = self.device.port
                        return
                    self.device.close()
                except Exception, e:
                    print e.__str__()

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

    ##Measurement Commands####################################################
    def measure_FTP(self, flow=True, temp=True, press=True, samples=1):
        """!
        Measure the flow temperature and pressure at the sample rate.
        @param self The pointer for the object
        @param samples The number of samples to return at the specified sample
        rate. Note that the minimum number of samples is 1 and the maximum is
        9999, sample values entered outside of these values are capped at the
        closest limit.
        @return a dictionary of lists containing the results for each of the
        specified test types.  The keys of the dictionary are 'flow', 'temp'
        and/or 'press' depending upon the tests selected
        """
        if samples <= 0:
            signed_samples = 1
        if samples > 9999:
            signed_samples = 9999
        sample_str_len = len(str(int(samples)))
        if (sample_str_len < 4):
            adjusted_samples = '0' * (4 - sample_str_len) + \
                               '%d' % signed_samples
        else:
            adjusted_samples = str(signed_samples)
        #From the Communications Protocol
        #D Denotes data transfer
        #C denotes ASCII format followed by CRLF
        #F requests a flow reading
        #T requests a temperature reading
        #P requests a pressure reading
        #The final term is the number of samples to collected at the specified
        #sample rate
        message_prefix = 'DC'
        #Manage the measurement selection
        #A lower case x represents not selecting a given measurement type
        if flow:
            message_prefix += 'F'
        else:
            message_prefix += 'x'
        if temp:
            message_prefix += 'T'
        else:
            message_prefix += 'x'
        if press:
            message_prefix += 'P'
        else:
            message_prefix += 'x'
        #If no tests are selected return None
        if (not flow) and (not temp) and (not press):
            return None
        #Append the number of samples
        message_prefix += 's' % adjusted_samples
        self.send_msg(message_prefix)
        acknowledge = self.read_msg()
        if acknowledge == 'OK':
            #Create a dictionary of lists to store the result
            result_dict = {}
            if flow:
                result_dict['flow'] = []
            if temp:
                result_dict['temp'] = []
            if press:
                result_dict['press'] = []
            #Loop through to get all of the available results
            while True:
                #Read the results from the device
                result = self.read_msg()
                if result is not '':
                    #Split the results into a list
                    result = result.split(',')
                    #Add the data to the results
                    #There are a number of different cobinations in which the
                    #results can be returned depending upon the measurement
                    #type selection
                    #The measurement results are provided in the following
                    #order:
                    #1. Flow measurements
                    #2. Temperature measurements
                    #3. Pressure measurements
                    if flow:
                        #Flow selected
                        result_dict['flow'].append(float(result[0]))
                        if temp:
                            result_dict['temp'].append(float(result[1]))
                            if press:
                                #All three measurement types are selected
                                result_dict['press'].append(float(result[2]))
                            else:
                                #Flow and temperature only
                                pass
                        else:
                            #Temp not selected
                            if press:
                                #Flow and pressure but not temperature
                                result_dict['press'].append(float(result[1]))
                            else:
                                #Flow only
                                pass
                    else:
                        #Flow not selected
                        if temp:
                            result_dict['temp'].append(float(result[0]))
                            if press:
                                #Temp and pressure not flow
                                result_dict['press'].append(float(result[1]))
                            else:
                                #Temperature only
                                pass
                        else:
                            #Temp not selected
                            if press:
                                #Pressure only selected
                                result_dict['press'].append(float(result[0]))
                            else:
                                #Nothing selected
                                #The method should not get here None should
                                #be returned prior to this point
                                pass

                else:
                    #The data has been retrieved, return
                    return result_dict
        else:
            if acknowledge.find('ERR') > 0:
                error = acknowledge.strip('ERR')
                err_msg = 'Error %d returned requesting measurement' %\
                          error
            else:
                err_msg = 'Unknown response received: %s' % err_msg
            raise TSIException(err_msg)

    def measure_volume(self, samples=1):
        """!
        Return a volume measurement by integrating flow rate over time
        @param self The pointer for the object
        @param samples The number of samples to return at the specified sample
        rate
        @return a list containing the returned results
        """
        #Check the sample number has been entered correctly
        if samples <= 0:
            signed_samples = 1
        if samples > 9999:
            signed_samples = 9999
        sample_str_len = len(str(int(samples)))
        if (sample_str_len < 4):
            adjusted_samples = '0' * (4 - sample_str_len) + \
                               '%d' % signed_samples
        else:
            adjusted_samples = str(signed_samples)
        #Create the message to send the device
        #According to the communications protocol
        #V denotes volume measurement
        #A denotes ASCII format
        #The final term is the number of samples to collected at the specified
        #sample rate
        message = 'VA%s' % adjusted_samples
        #Send the message to the device
        self.send_msg(message)
        acknowledge = self.read_msg()
        results_list = []
        if acknowledge == 'OK':
            #Response correctly received
            while True:
                response = self.read_msg()
                if response is not '':
                    results_list.append(float(response))
                else:
                    return results_list
        else:
            #An error occurred
            if acknowledge.find('ERR') > 0:
                error = acknowledge.strip('ERR')
                err_msg = 'Error %d returned requesting measurement' %\
                          error
            else:
                err_msg = 'Unknown response received: %s' % err_msg
            raise TSIException(err_msg)

    ##Configuration Commands###################################################
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
        if rate >= 1000:
            signed_rate = 1000
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
                err_msg = 'Unknown response received: %s' % err_msg
            raise TSIException(err_msg)

    #def set_trigger_level(self, source=