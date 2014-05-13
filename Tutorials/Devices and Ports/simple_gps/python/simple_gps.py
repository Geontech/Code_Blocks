#!/usr/bin/env python
#
# AUTO-GENERATED
#
# Source: simple_gps.spd.xml
from ossie.device import start_device
import logging

from simple_gps_base import *

# Code Snip 1-3 -- Create the IDL structures from these links or just lift it from my gist:
# [link][https://gist.github.com/btgoodwin/9917abe1db234869a9b8]

import bulkio
# https://github.com/RedhawkSDR/frontendInterfaces/blob/develop-2.2/Frontend.idl
class PositionInfo:
    valid   = False
    datum   = ''
    lat     = 0.0
    lon     = 0.0
    alt     = 0.0
    
# https://github.com/RedhawkSDR/frontendInterfaces/blob/develop-2.2/GPS.idl
class GPSInfo:
    source_id       = ''
    rf_flow_id      = ''
    mode            = ''
    fom             = 0
    tfom            = 0
    datumID         = 0
    time_offset     = 0.0
    freq_offset     = 0.0
    time_variance   = 0.0
    freq_variance   = 0.0
    satellite_count = 0
    snr             = 0.0
    status_message  = ''
    timestamp       = bulkio.timestamp.now()
    additional_info = None

class GpsTimePos:
    position    = PositionInfo()
    timestamp   = bulkio.timestamp.now()
        
# Code Snip 4 from base class to protect against code generation
class My_PortFRONTENDGPSIn(PortFRONTENDGPSIn_i):
    def _get_gps_info(self):
        return self.parent.GPSInfo
    
    def _get_gps_time_pos(self):
        return self.parent.GpsTimePos


class simple_gps_i(simple_gps_base):
    """<DESCRIPTION GOES HERE>"""
    def initialize(self):
        """
        This is called by the framework immediately after your device registers with the NameService.
        
        In general, you should add customization here and not in the __init__ constructor.  If you have 
        a custom port implementation you can override the specific implementation here with a statement
        similar to the following:
          self.some_port = MyPortImplementation()
        """
        simple_gps_base.initialize(self)
        
        # Code Snip 5 -- Replace port with our subclass and add the GPS structures
        self.port_GPS_idl = My_PortFRONTENDGPSIn(self, "GPS_idl")
        self._GpsTimePos = GpsTimePos()
        self._GPSInfo = GPSInfo()
    
    # Code Snip 6a and b -- public properties to return the structures.
    @property
    def GpsTimePos(self):
        return self._GpsTimePos
    
    @property
    def GPSInfo(self):
        return self._GPSInfo
        
    #Code Snip 7 -- auto-start for the service function
    def configure(self, configProperties):
        simple_gps_base.configure(self, configProperties)
        if (not self._get_started()):
             self.start()
        
    def updateUsageState(self):
        """
        This is called automatically after allocateCapacity or deallocateCapacity are called.
        Your implementation should determine the current state of the device:
           self._usageState = CF.Device.IDLE   # not in use
           self._usageState = CF.Device.ACTIVE # in use, with capacity remaining for allocation
           self._usageState = CF.Device.BUSY   # in use, with no capacity remaining for allocation
        """
        return NOOP


    def process(self):
        """
        Basic functionality:
        
            The process method should process a single "chunk" of data and then return. This method
            will be called from the processing thread again, and again, and again until it returns
            FINISH or stop() is called on the device.  If no work is performed, then return NOOP.
            
        StreamSRI:
            To create a StreamSRI object, use the following code (this generates a normalized SRI that does not flush the queue when full):
                self.sri = bulkio.sri.create(self.stream_id)

        PrecisionUTCTime:
            To create a PrecisionUTCTime object, use the following code:
                tstamp = bulkio.timestamp.now() 
  
        Ports:

            Each port instance is accessed through members of the following form: self.port_<PORT NAME>
            
            Data is obtained in the process function through the getPacket call (BULKIO only) on a
            provides port member instance. The getPacket function call is non-blocking - if no data
            is available, it will return immediately with all values == None.
            
            To send data, call the appropriate function in the port directly. In the case of BULKIO,
            convenience functions have been added in the port classes that aid in output.
            
            Interactions with non-BULKIO ports are left up to the device developer's discretion.
            
        Properties:
        
            Properties are accessed directly as member variables. If the property name is baudRate,
            then accessing it (for reading or writing) is achieved in the following way: self.baudRate.
            
        Example:
        
            # This example assumes that the device has two ports:
            #   - A provides (input) port of type bulkio.InShortPort called dataShort_in
            #   - A uses (output) port of type bulkio.OutFloatPort called dataFloat_out
            # The mapping between the port and the class if found in the device
            # base class.
            # This example also makes use of the following Properties:
            #   - A float value called amplitude
            #   - A boolean called increaseAmplitude
            
            data, T, EOS, streamID, sri, sriChanged, inputQueueFlushed = self.port_dataShort_in.getPacket()
            
            if data == None:
                return NOOP
                
            outData = range(len(data))
            for i in range(len(data)):
                if self.increaseAmplitude:
                    outData[i] = float(data[i]) * self.amplitude
                else:
                    outData[i] = float(data[i])
                
            # NOTE: You must make at least one valid pushSRI call
            if sriChanged:
                self.port_dataFloat_out.pushSRI(sri);

            self.port_dataFloat_out.pushPacket(outData, T, EOS, streamID)
            return NORMAL
            
        """
        # Code Snip 8 -- Make-believe GPS ingest. 
        self._GPSInfo.timestamp = self._GpsTimePos.timestamp = bulkio.timestamp.now()
        
        return NOOP
  
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARN)
    logging.debug("Starting Device")
    start_device(simple_gps_i)

