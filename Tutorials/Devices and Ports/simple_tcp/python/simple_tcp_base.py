#!/usr/bin/env python
#
# AUTO-GENERATED CODE.  DO NOT MODIFY!
#
# Source: simple_tcp.spd.xml
from ossie.cf import CF, CF__POA
from ossie.utils import uuid

from ossie.device import Device
from ossie.properties import simple_property

import Queue, copy, time, threading
from ossie.resource import usesport, providesport
import bulkio
from redhawk.frontendInterfaces import FRONTEND

NOOP = -1
NORMAL = 0
FINISH = 1
class ProcessThread(threading.Thread):
    def __init__(self, target, pause=0.0125):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.target = target
        self.pause = pause
        self.stop_signal = threading.Event()

    def stop(self):
        self.stop_signal.set()

    def updatePause(self, pause):
        self.pause = pause

    def run(self):
        state = NORMAL
        while (state != FINISH) and (not self.stop_signal.isSet()):
            state = self.target()
            delay = 1e-6
            if (state == NOOP):
                # If there was no data to process sleep to avoid spinning
                delay = self.pause
            time.sleep(delay)

class simple_tcp_base(CF__POA.Device, Device):
        # These values can be altered in the __init__ of your derived class

        PAUSE = 0.0125 # The amount of time to sleep if process return NOOP
        TIMEOUT = 5.0 # The amount of time to wait for the process thread to die when stop() is called
        DEFAULT_QUEUE_SIZE = 100 # The number of BulkIO packets that can be in the queue before pushPacket will block

        def __init__(self, devmgr, uuid, label, softwareProfile, compositeDevice, execparams):
            Device.__init__(self, devmgr, uuid, label, softwareProfile, compositeDevice, execparams)
            self.threadControlLock = threading.RLock()
            self.process_thread = None
            # self.auto_start is deprecated and is only kept for API compatibility
            # with 1.7.X and 1.8.0 devices.  This variable may be removed
            # in future releases
            self.auto_start = False

        def initialize(self):
            Device.initialize(self)
            
            # Instantiate the default implementations for all ports on this device
            self.port_dataFloat_out = bulkio.OutFloatPort("dataFloat_out")
            self.port_GPS_uses = PortFRONTENDGPSOut_i(self, "GPS_uses")

        def start(self):
            self._log.info("Base start() called")
            self.threadControlLock.acquire()
            try:
                Device.start(self)
                if self.process_thread == None:
                    self.process_thread = ProcessThread(target=self.process, pause=self.PAUSE)
                    self.process_thread.start()
            finally:
                self.threadControlLock.release()

        def process(self):
            """The process method should process a single "chunk" of data and then return.  This method will be called
            from the processing thread again, and again, and again until it returns FINISH or stop() is called on the
            device.  If no work is performed, then return NOOP"""
            raise NotImplementedError

        def stop(self):
            self._log.info("Base stop() called")
            self.threadControlLock.acquire()
            try:
                process_thread = self.process_thread
                self.process_thread = None

                if process_thread != None:
                    process_thread.stop()
                    process_thread.join(self.TIMEOUT)
                    if process_thread.isAlive():
                        raise CF.Resource.StopError(CF.CF_NOTSET, "Processing thread did not die")
                Device.stop(self)
            finally:
                self.threadControlLock.release()

        def releaseObject(self):
            try:
                self.stop()
            except Exception:
                self._log.exception("Error stopping")
            self.threadControlLock.acquire()
            try:
                Device.releaseObject(self)
            finally:
                self.threadControlLock.release()

        ######################################################################
        # PORTS
        # 
        # DO NOT ADD NEW PORTS HERE.  You can add ports in your derived class, in the SCD xml file, 
        # or via the IDE.

        # 'FRONTEND/GPS' port
        class PortFRONTENDGPSOut(CF__POA.Port):
            """This class is a port template for the PortFRONTENDGPSOut_i port and
            should not be instantiated nor modified.
            
            The expectation is that the specific port implementation will extend
            from this class instead of the base CORBA class CF__POA.Port.
            """
            pass

        port_dataFloat_out = usesport(name="dataFloat_out",
                                      repid="IDL:BULKIO/dataFloat:1.0",
                                      type_="control")

        port_GPS_uses = usesport(name="GPS_uses",
                                 repid="IDL:FRONTEND/GPS:1.0",
                                 type_="control")

        ######################################################################
        # PROPERTIES
        # 
        # DO NOT ADD NEW PROPERTIES HERE.  You can add properties in your derived class, in the PRF xml file
        # or by using the IDE.
        device_kind = simple_property(id_="DCE:cdc5ee18-7ceb-4ae6-bf4c-31f983179b4d",
                                      name="device_kind",
                                      type_="string",
                                      defvalue="socket",
                                      mode="readonly",
                                      action="eq",
                                      kinds=("allocation","configure"),
                                      description="""This specifies the device kind"""
                                      )
        device_model = simple_property(id_="DCE:0f99b2e4-9903-4631-9846-ff349d18ecfb",
                                       name="device_model",
                                       type_="string",
                                       defvalue="tcp",
                                       mode="readonly",
                                       action="eq",
                                       kinds=("allocation","configure"),
                                       description=""" This specifies the specific device"""
                                       )
        port_num = simple_property(id_="port_num",
                                   name="port_num",
                                   type_="ulong",
                                   defvalue=9999,
                                   mode="readwrite",
                                   action="external",
                                   kinds=("configure",)                                 )

'''uses port(s)'''

class PortFRONTENDGPSOut_i(simple_tcp_base.PortFRONTENDGPSOut):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.outConnections = {}
        self.port_lock = threading.Lock()

    def connectPort(self, connection, connectionId):
        self.port_lock.acquire()
        try:
            port = connection._narrow(FRONTEND.GPS)
            self.outConnections[str(connectionId)] = port
        finally:
            self.port_lock.release()

    def disconnectPort(self, connectionId):
        self.port_lock.acquire()
        try:
            self.outConnections.pop(str(connectionId), None)
        finally:
            self.port_lock.release()

    def _get_gps_info(self):
        retVal = None
        self.port_lock.acquire()

        try:
            for connId, port in self.outConnections.items():
                if port != None:
                    try:
                        retVal = port._get_gps_info()
                    except Exception:
                        self.parent._log.exception("The call to _get_gps_info failed on port %s connection %s instance %s", self.name, connId, port)
        finally:
            self.port_lock.release()

        return retVal

    def _set_gps_info(self, data):
        self.port_lock.acquire()

        try:
            for connId, port in self.outConnections.items():
                if port != None:
                    try:
                        port._set_gps_info(data)
                    except Exception:
                        self.parent._log.exception("The call to _set_gps_info failed on port %s connection %s instance %s", self.name, connId, port)
        finally:
            self.port_lock.release()

    def _get_gps_time_pos(self):
        retVal = None
        self.port_lock.acquire()

        try:
            for connId, port in self.outConnections.items():
                if port != None:
                    try:
                        retVal = port._get_gps_time_pos()
                    except Exception:
                        self.parent._log.exception("The call to _get_gps_time_pos failed on port %s connection %s instance %s", self.name, connId, port)
        finally:
            self.port_lock.release()

        return retVal

    def _set_gps_time_pos(self, data):
        self.port_lock.acquire()

        try:
            for connId, port in self.outConnections.items():
                if port != None:
                    try:
                        port._set_gps_time_pos(data)
                    except Exception:
                        self.parent._log.exception("The call to _set_gps_time_pos failed on port %s connection %s instance %s", self.name, connId, port)
        finally:
            self.port_lock.release()

