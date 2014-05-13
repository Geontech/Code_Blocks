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