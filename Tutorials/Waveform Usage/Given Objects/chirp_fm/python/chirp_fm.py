#!/usr/bin/env python
#
# AUTO-GENERATED
#
# Source: chirp_fm.spd.xml
from ossie.device import start_device
import logging

from chirp_fm_base import *

import numpy as np
from scipy.signal import chirp
import csv

class chirp_fm_i(chirp_fm_base):
    """<DESCRIPTION GOES HERE>"""
    def setupSignal(self):
        # Chirp is passed through FM modulation via phase since the two are
        # inseparable.
        tvec = np.linspace(0.0, self.chirp.duration * 4.0, self.fs)
        base = self.chirp.amplitude * 10.0 * np.cos(2.0 * np.pi * self.fmod * tvec)

        cvec = []
        for idx, t in enumerate(tvec):
            cvec.append(chirp(np.array([t]), 
                              f0=self.chirp.fstart, 
                              t1=self.chirp.duration, 
                              f1=self.chirp.fstop,
                              phi=base[idx])[0])
                
        self._signal = self.chirp.amplitude * np.array(cvec)
        
        if (self.debug_vector):
            ps = np.abs(np.fft.fft(self._signal))
            freqs = np.fft.fftfreq(self._signal.size, 1.0/self.fs)
            idx = np.argsort(freqs)
            
            with open("vector.csv", "wb") as f:
                writer = csv.writer(f)
                writer.writerows([tvec, base, self._signal, freqs[idx], ps[idx]])
        
    def onconfigure_prop_chirp(self, old, new):
        self.chirp = new
        self.setupSignal()
        
    def allocate_throttle(self, value):
        self.throttle = abs(value)
        return True
    
    def allocate_os_name(self, value):
        return True
    
    def allocate_processor_name(self, value):
        return True 
    
    def initialize(self):
        """
        This is called by the framework immediately after your device registers with the NameService.
        
        In general, you should add customization here and not in the __init__ constructor.  If you have 
        a custom port implementation you can override the specific implementation here with a statement
        similar to the following:
          self.some_port = MyPortImplementation()
        """
        chirp_fm_base.initialize(self)
        self._last_time = time.time()
        self._send_SRI = True
        self._stream_ID = "tweet"

    def configure(self, configProperties):
        chirp_fm_base.configure(self, configProperties)
        
        if not self._started:
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

        # TODO fill in your code here
        """ Every throttled window will output a sample vector """
        if (time.time() - self._last_time > self.throttle / self.fs):
            self._last_time = time.time()
            
            if (self._send_SRI):
                self.sri = bulkio.sri.create(self._stream_ID)
                self.sri.mode = 1;            # Complex
                self.sri.xdelta = 1.0/self.fs # Time delta between samples.
                self.port_dataFloat_out.pushSRI(self.sri)
                self._send_SRI = False
            
            vec = list(self._signal[0:self.throttle])
            self._signal = np.roll(self._signal, -self.throttle)
            
            tstamp = bulkio.timestamp.now()
            self.port_dataFloat_out.pushPacket(vec, tstamp, False, self._stream_ID)            
            retval = NORMAL
            
        else:
            retval = NOOP
        
        return retval
        
  
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARN)
    logging.debug("Starting Device")
    start_device(chirp_fm_i)

