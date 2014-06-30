#!/usr/bin/env python
#
# AUTO-GENERATED
#
# Source: sawtooth_device.spd.xml
from ossie.device import start_device
import logging

from sawtooth_device_base import *

from scipy import signal
import numpy as np

class sawtooth_device_i(sawtooth_device_base):
    """<DESCRIPTION GOES HERE>"""
    
    sendSRI = True
    data = None
    lastTime = None
    
    def initialize(self):
        """
        This is called by the framework immediately after your device registers with the NameService.
        
        In general, you should add customization here and not in the __init__ constructor.  If you have 
        a custom port implementation you can override the specific implementation here with a statement
        similar to the following:
          self.some_port = MyPortImplementation()
        """
        sawtooth_device_base.initialize(self)
        self.control_params.frequency = self.control_params.amplitude = 0.0
        self.port_message.registerMessage("control_params",
                                          sawtooth_device_base.ControlParams,
                                          self.control_params_received)
        
    def freq_is_valid(self, fs=None, freq=None):
        if (None == fs):
            fs = self.sample_freq
        if (None == freq):
            freq = self.control_params.frequency
            
        return (fs >= freq * 2.0)
        
    def control_params_received(self, msgID, newval):
        if (self.freq_is_valid(freq=newval.frequency)):
            self.control_params = newval;
            self.data = None;
        
    def allocate_sample_freq(self, value):
        valid = True
        if (not self.freq_is_valid(fs=value) or
            (CF.Device.BUSY == self._get_usageState())):
            valid = False
        else:
            self.sample_freq = value
            if (not self._get_started()):
                self.start()
        return valid
    
    def deallocate_sample_freq(self, value):
        if (CF.Device.BUSY == self._get_usageState()):
            self.stop()
        
    def updateUsageState(self):
        """
        This is called automatically after allocateCapacity or deallocateCapacity are called.
        Your implementation should determine the current state of the device:
           self._usageState = CF.Device.IDLE   # not in use
           self._usageState = CF.Device.ACTIVE # in use, with capacity remaining for allocation
           self._usageState = CF.Device.BUSY   # in use, with no capacity remaining for allocation
        """
        if (self._get_started()):
            self._usageState = CF.Device.BUSY
        else:
            self._usageState = CF.Device.IDLE
            
        return NOOP

    def stop(self):
        sawtooth_device_base.stop(self)
        self.data = None

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
        state = NOOP
        stream_id = "ramp_func"
        
        if (self.sendSRI):
            sri = bulkio.sri.create(stream_id)
            sri.xdelta = 1.0 / self.sample_freq
            self.port_dataFloat_out.pushSRI(sri)
            self.sendSRI = False 
        
        tstamp = bulkio.timestamp.now()
        vec = self.getData(tstamp)
        
        if (None != vec):
            self.port_dataFloat_out.pushPacket(vec, tstamp, False, stream_id)
            state = NORMAL
        
        return state
    
    def getData(self, tstamp):
        if (None == self.data):
            t = np.linspace(0, 1, self.sample_freq)
            self.data = signal.sawtooth(2 * np.pi * self.control_params.frequency * t)
            self.data = self.data * self.control_params.amplitude
        
        if (None == self.lastTime):
            self.lastTime = bulkio.timestamp.now()
        
        t_then = self.lastTime.twsec + self.lastTime.tfsec
        t_now = tstamp.twsec + tstamp.tfsec
        
        vec = None

        if (t_now - t_then >= self.window / self.sample_freq):
            vec = list(self.data[0:self.window])
            self.data = np.roll(self.data, -self.window)
            self.lastTime = tstamp
            
        return vec
        
  
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARN)
    logging.debug("Starting Device")
    start_device(sawtooth_device_i)

