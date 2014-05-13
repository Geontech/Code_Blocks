'''  SNIP 1 : above simple_tcp_i '''
import SocketServer

# Simple class to handle the brief life cycle of a socket
class DataReceiver (SocketServer.StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline().strip()
        self.server.addData(data)

''' SNIP 2 : within simple_tcp_i '''
def configure(self, configProperties):
    simple_tcp_base.configure(self, configProperties)
    self.start()

''' SNIP 3  : within simple_tcp_i '''
def onconfigure_prop_port_num(self, oldval, newval):
    self.port_num = newval
    if (self._get_started()):
        self.stop()
        self.start()

''' SNIP 4 : within simple_tcp_i '''
def start(self):
    self._sendSRI = True
    self._server = MyThreadedTCPServer(('', self.port_num), DataReceiver)
    server_thread = threading.Thread(target=self._server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    simple_tcp_base.start(self)
    
def stop(self):
    if (None != self._server):
        self._server.shutdown()
        self._server = None
    simple_tcp_base.stop(self)

''' SNIP 5 : within simple_tcp_i '''
def process(self):
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

        self.port_dataFloat_out.pushPacket(data, utcNow, False, streamID)
            
    return returnCode
