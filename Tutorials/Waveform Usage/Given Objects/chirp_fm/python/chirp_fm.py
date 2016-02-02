#!/usr/bin/env python
#
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
        
    def chirp_callback(self, id_, old, new):
        self.chirp = new
        self.setupSignal()
        
    def allocate_throttle(self, value):
        if 0 < value:
            self.throttle = value
            return True
        return False
    
    def deallocate_throttle(self, value):
        pass
    
    def constructor(self):
        """
        This is called by the framework immediately after your device registers with the system.
        
        In general, you should add customization here and not in the __init__ constructor.  If you have 
        a custom port implementation you can override the specific implementation here with a statement
        similar to the following:
          self.some_port = MyPortImplementation()

        """
        self._last_time = time.time()
        self._send_SRI = True
        self._stream_ID = "tweet"
        
        self.addPropertyChangeListener('chirp', self.chirp_callback)
        self.setAllocationImpl("throttle", self.allocate_throttle, self.deallocate_throttle)
        
        if not self._started:
            self.setupSignal()
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
            provides port member instance. The optional argument is a timeout value, in seconds.
            A zero value is non-blocking, while a negative value is blocking. Constants have been
            defined for these values, bulkio.const.BLOCKING and bulkio.const.NON_BLOCKING. If no
            timeout is given, it defaults to non-blocking.
            
            The return value is a named tuple with the following fields:
                - dataBuffer
                - T
                - EOS
                - streamID
                - SRI
                - sriChanged
                - inputQueueFlushed
            If no data is available due to a timeout, all fields are None.

            To send data, call the appropriate function in the port directly. In the case of BULKIO,
            convenience functions have been added in the port classes that aid in output.
            
            Interactions with non-BULKIO ports are left up to the device developer's discretion.
            
        Messages:
    
            To receive a message, you need (1) an input port of type MessageEvent, (2) a message prototype described
            as a structure property of kind message, (3) a callback to service the message, and (4) to register the callback
            with the input port.
        
            Assuming a property of type message is declared called "my_msg", an input port called "msg_input" is declared of
            type MessageEvent, create the following code:
        
            def msg_callback(self, msg_id, msg_value):
                print msg_id, msg_value
        
            Register the message callback onto the input port with the following form:
            self.port_input.registerMessage("my_msg", chrip_fm_i.MyMsg, self.msg_callback)
        
            To send a message, you need to (1) create a message structure, and (2) send the message over the port.
        
            Assuming a property of type message is declared called "my_msg", an output port called "msg_output" is declared of
            type MessageEvent, create the following code:
        
            msg_out = chrip_fm_i.MyMsg()
            this.port_msg_output.sendMessage(msg_out)

        Properties:
        
            Properties are accessed directly as member variables. If the property name is baudRate,
            then accessing it (for reading or writing) is achieved in the following way: self.baudRate.

            To implement a change callback notification for a property, create a callback function with the following form:

            def mycallback(self, id, old_value, new_value):
                pass

            where id is the property id, old_value is the previous value, and new_value is the updated value.
            
            The callback is then registered on the component as:
            self.addPropertyChangeListener('baudRate', self.mycallback)
            
        Allocation:
            
            Allocation callbacks are available to customize a Device's response to an allocation request. 
            Callback allocation/deallocation functions are registered using the setAllocationImpl function,
            usually in the initialize() function
            For example, allocation property "my_alloc" can be registered with allocation function 
            my_alloc_fn and deallocation function my_dealloc_fn as follows:
            
            self.setAllocationImpl("my_alloc", self.my_alloc_fn, self.my_dealloc_fn)
            
            def my_alloc_fn(self, value):
                # perform logic
                return True # successful allocation
            
            def my_dealloc_fn(self, value):
                # perform logic
                pass
            
        Example:
        
            # This example assumes that the device has two ports:
            #   - A provides (input) port of type bulkio.InShortPort called dataShort_in
            #   - A uses (output) port of type bulkio.OutFloatPort called dataFloat_out
            # The mapping between the port and the class if found in the device
            # base class.
            # This example also makes use of the following Properties:
            #   - A float value called amplitude
            #   - A boolean called increaseAmplitude
            
            packet = self.port_dataShort_in.getPacket()
            
            if packet.dataBuffer is None:
                return NOOP
                
            outData = range(len(packet.dataBuffer))
            for i in range(len(packet.dataBuffer)):
                if self.increaseAmplitude:
                    outData[i] = float(packet.dataBuffer[i]) * self.amplitude
                else:
                    outData[i] = float(packet.dataBuffer[i])
                
            # NOTE: You must make at least one valid pushSRI call
            if packet.sriChanged:
                self.port_dataFloat_out.pushSRI(packet.SRI);

            self.port_dataFloat_out.pushPacket(outData, packet.T, packet.EOS, packet.streamID)
            return NORMAL
            
        """
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
    logging.getLogger().setLevel(logging.INFO)
    logging.debug("Starting Device")
    start_device(chirp_fm_i)

