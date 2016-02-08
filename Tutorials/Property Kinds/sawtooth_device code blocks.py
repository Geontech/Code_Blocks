# PART 1
''' Block 1: sawtooth_device_i class '''
        self.addPropertyChangeListener('control_params', self.control_params_changed)

    def control_params_changed(self, prop_id, oldval, newval):
        if (self.freq_is_valid(freq=newval.frequency)):
            self.control_params = newval;
            self.data = None;

# PART 2
''' Block 1: sawtooth_device_i '''
    # Delete "sample_freq" initial value from the class and add allocated.  Result would be:
    sendSRI = True
    allocations_available = True
    data = None
    lastTime = None

''' Block 2: sawtooth_device_i.constructor() changes '''
        # Append to the body:
        self.setAllocationImpl("sample_freq", 
            self.allocate_sample_freq, 
            self.deallocate_sample_freq)

''' Block 3: sawtooth_device_i '''
    def allocate_sample_freq(self, value):
        valid = True
        if (not self.freq_is_valid(fs=value) or
            (CF.Device.BUSY == self._get_usageState())):
            valid = False
        else:
            self.sample_freq = value
            self.allocations_available = False
            if (not self._get_started()):
                self.start()
        return valid

    def deallocate_sample_freq(self, value):
        if (CF.Device.BUSY == self._get_usageState()):
            self.allocations_available = True
            self.stop()

''' Block 4: sawtooth_device_i '''
        # Body of updateUsageState()
        if not self.allocations_available:
            self._usageState = CF.Device.BUSY
        else:
            self._usageState = CF.Device.IDLE

''' Block 5: sawtooth_device_i.getData() changes '''
        # Delete "count" and change "count" to "self.window" thereafter
        vec = None

        if (t_now - t_then >= self.window / self.sample_freq):
            vec = list(self.data[0:self.window])
            self.data = np.roll(self.data, -self.window)
            self.lastTime = tstamp
        

# PART 3
''' Block 1: sawtooth_device_i control_params_changed replaced with: '''
    # Modify the control_params_changed to this method
    def control_params_received(self, msgID, newval):
        if (self.freq_is_valid(freq=newval.frequency)):
            self.control_params = newval;
            self.data = None;

''' Block 2: sawtooth_device_i.construtor() after base class call '''
    # In constructor() delete the addPropertyChangeListener call
        self.control_params.frequency = self.control_params.amplitude = 0.0
        self.port_message.registerMessage("control_params",
                                          sawtooth_device_base.ControlParams,
                                          self.control_params_received)