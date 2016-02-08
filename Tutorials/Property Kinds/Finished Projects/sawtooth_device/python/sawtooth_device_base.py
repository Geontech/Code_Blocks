#!/usr/bin/env python
#
# AUTO-GENERATED CODE.  DO NOT MODIFY!
#
# Source: sawtooth_device.spd.xml
from ossie.cf import CF
from ossie.cf import CF__POA
from ossie.utils import uuid

from ossie.device import Device
from ossie.threadedcomponent import *
from ossie.properties import simple_property
from ossie.properties import simpleseq_property
from ossie.properties import struct_property

import Queue, copy, time, threading
from ossie.resource import usesport, providesport
from ossie.events import MessageConsumerPort
import bulkio

class sawtooth_device_base(CF__POA.Device, Device, ThreadedComponent):
        # These values can be altered in the __init__ of your derived class

        PAUSE = 0.0125 # The amount of time to sleep if process return NOOP
        TIMEOUT = 5.0 # The amount of time to wait for the process thread to die when stop() is called
        DEFAULT_QUEUE_SIZE = 100 # The number of BulkIO packets that can be in the queue before pushPacket will block

        def __init__(self, devmgr, uuid, label, softwareProfile, compositeDevice, execparams):
            Device.__init__(self, devmgr, uuid, label, softwareProfile, compositeDevice, execparams)
            ThreadedComponent.__init__(self)

            # self.auto_start is deprecated and is only kept for API compatibility
            # with 1.7.X and 1.8.0 devices.  This variable may be removed
            # in future releases
            self.auto_start = False
            # Instantiate the default implementations for all ports on this device
            self.port_message = MessageConsumerPort(thread_sleep=0.1, parent = self)
            self.port_dataFloat_out = bulkio.OutFloatPort("dataFloat_out")

        def start(self):
            Device.start(self)
            ThreadedComponent.startThread(self, pause=self.PAUSE)

        def stop(self):
            Device.stop(self)
            if not ThreadedComponent.stopThread(self, self.TIMEOUT):
                raise CF.Resource.StopError(CF.CF_NOTSET, "Processing thread did not die")

        def releaseObject(self):
            try:
                self.stop()
            except Exception:
                self._log.exception("Error stopping")
            Device.releaseObject(self)

        ######################################################################
        # PORTS
        # 
        # DO NOT ADD NEW PORTS HERE.  You can add ports in your derived class, in the SCD xml file, 
        # or via the IDE.

        port_message = providesport(name="message",
                                    repid="IDL:ExtendedEvent/MessageEvent:1.0",
                                    type_="control")

        port_dataFloat_out = usesport(name="dataFloat_out",
                                      repid="IDL:BULKIO/dataFloat:1.0",
                                      type_="data")

        ######################################################################
        # PROPERTIES
        # 
        # DO NOT ADD NEW PROPERTIES HERE.  You can add properties in your derived class, in the PRF xml file
        # or by using the IDE.
        device_kind = simple_property(id_="DCE:cdc5ee18-7ceb-4ae6-bf4c-31f983179b4d",
                                      name="device_kind",
                                      type_="string",
                                      mode="readonly",
                                      action="eq",
                                      kinds=("allocation",),
                                      description="""This specifies the device kind""")
        
        device_model = simple_property(id_="DCE:0f99b2e4-9903-4631-9846-ff349d18ecfb",
                                       name="device_model",
                                       type_="string",
                                       mode="readonly",
                                       action="eq",
                                       kinds=("allocation",),
                                       description=""" This specifies the specific device""")
        
        window = simple_property(id_="window",
                                 type_="ushort",
                                 defvalue=100,
                                 mode="readonly",
                                 action="external",
                                 kinds=("property",))
        
        sample_freq = simple_property(id_="sample_freq",
                                      type_="float",
                                      defvalue=100000.0,
                                      mode="readwrite",
                                      action="external",
                                      kinds=("allocation",))
        
        class ControlParams(object):
            amplitude = simple_property(
                                        id_="amplitude",
                                        type_="float",
                                        defvalue=10.0
                                        )
        
            frequency = simple_property(
                                        id_="frequency",
                                        type_="float",
                                        defvalue=500.0
                                        )
        
            def __init__(self, **kw):
                """Construct an initialized instance of this struct definition"""
                for classattr in type(self).__dict__.itervalues():
                    if isinstance(classattr, (simple_property, simpleseq_property)):
                        classattr.initialize(self)
                for k,v in kw.items():
                    setattr(self,k,v)
        
            def __str__(self):
                """Return a string representation of this structure"""
                d = {}
                d["amplitude"] = self.amplitude
                d["frequency"] = self.frequency
                return str(d)
        
            @classmethod
            def getId(cls):
                return "control_params"
        
            @classmethod
            def isStruct(cls):
                return True
        
            def getMembers(self):
                return [("amplitude",self.amplitude),("frequency",self.frequency)]
        
        control_params = struct_property(id_="control_params",
                                         structdef=ControlParams,
                                         configurationkind=("message",),
                                         mode="readwrite")
        


