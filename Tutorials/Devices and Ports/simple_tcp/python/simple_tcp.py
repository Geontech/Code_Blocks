#!/usr/bin/env python
#
# AUTO-GENERATED
#
# Source: simple_tcp.spd.xml
from ossie.device import start_device
import logging

from simple_tcp_base import *

import SocketServer

# Simple class to handle the brief life cycle of a socket
class DataReceiver (SocketServer.StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline().strip()
        self.server.addData(data)

# Extension of Threaded TCP server
class MyThreadedTCPServer (SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    # Local variables for storing the data array, lock, and sample period
    _data = list()
    _lock = threading.Lock()
    _averageSamplePeriod = 0.0
    
    def addData(self, newData):
        # Lock and save newData to _data.
        try:
            self._lock.acquire()            
            # Add newData to _data, average sample periods
            subs = newData.split(",")
            self._averageSamplePeriod += float(subs[0])
            self._averageSamplePeriod /= 2.0
            for s in subs[1:]:
                self._data.append(float(s))
                
        finally:
            self._lock.release()    
    
    # Returns all data since last call, start time, and
    # running average sample period
    def getDataAndSampleTime(self):
        outData = []
        outPeriod = 0.0
        try:
            self._lock.acquire()
            if (0 < len(self._data)):
                outData = self._data
                outPeriod = self._averageSamplePeriod
                
        finally:
            self._data = list()
            # Not clearing the _averageSamplePeriod
            self._lock.release()
            
        return outData, outPeriod


class simple_tcp_i(simple_tcp_base):
    # Properties
    _server = None
    _sendSRI = False
    
    """<DESCRIPTION GOES HERE>"""
    def initialize(self):
        """
        This is called by the framework immediately after your device registers with the NameService.
        
        In general, you should add customization here and not in the __init__ constructor.  If you have 
        a custom port implementation you can override the specific implementation here with a statement
        similar to the following:
          self.some_port = MyPortImplementation()
        """
        simple_tcp_base.initialize(self)
        # TODO add customization here.
    
    def onconfigure_prop_port_num(self, oldval, newval):
        self.port_num = newval
        if (self._get_started()):
            self.stop()
            self.start()
    
    def configure(self, configProperties):
        simple_tcp_base.configure(self, configProperties)
        if (not self._get_started()):
            self.start()
    
    def start(self):
        self._log.info("Own start() called")
        self._sendSRI = True
        self._server = MyThreadedTCPServer(('', self.port_num), DataReceiver)
        server_thread = threading.Thread(target=self._server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        simple_tcp_base.start(self)
        
    def stop(self):
        self._log.info("Own stop() called")
        if (None != self._server):
            self._server.shutdown()
            self._server = None
        simple_tcp_base.stop(self)
    
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
        streamID = "TCP port {0}".format(self.port_num)
        data, samplePeriod = self._server.getDataAndSampleTime()
        returnCode = NOOP
        
        if (0 < len(data)):
            returnCode = NORMAL
            
            utcNow = None
            gpsInfo = self.port_GPS_uses._get_gps_info()
            if (None != gpsInfo):
                utcNow = gpsInfo.timestamp        
            else:
                utcNow = bulkio.timestamp.now()
            
            if (self._sendSRI):
                sri = bulkio.sri.create(streamID)
                sri.xdelta = samplePeriod
                self.port_dataFloat_out.pushSRI(sri)
                self._sendSRI = False

            self.port_dataFloat_out.pushPacket(data, utcNow, 
                                               False, streamID)
            
        return returnCode        
  
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARN)
    logging.debug("Starting Device")
    start_device(simple_tcp_i)
