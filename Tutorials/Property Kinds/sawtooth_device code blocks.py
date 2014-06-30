# PART 1
''' Block 1: sawtooth_device_i class '''
    def onconfigure_prop_control_params(self, oldval, newval):
        if (self.freq_is_valid(freq=newval.frequency)):
            self.control_params = newval;
            self.data = None;

# PART 2
''' Block 1: sawtooth_device_i.getData() changes '''
        vec = None

        if (t_now - t_then >= self.window / self.sample_freq):
            vec = list(self.data[0:self.window])
            self.data = np.roll(self.data, -self.window)
            self.lastTime = tstamp

''' Block 2: sawtooth_device_i '''
# Delete "sample_freq" from the class.  Result would be:
sendSRI = True

data = None
lastTime = None

''' Block 3: sawtooth_device_i '''
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


''' Block 4: sawtooth_device_i '''
    def deallocate_sample_freq(self, value):
        if (CF.Device.BUSY == self._get_usageState()):
            self.stop()

# PART 3
''' Block 1: sawtooth_device_i onconfigure* replaced with: '''
    def control_params_received(self, msgID, newval):
        if (self.freq_is_valid(freq=newval.frequency)):
            self.control_params = newval;
            self.data = None;

''' Block 2: sawtooth_device_i.initialize() after base class call '''
        self.control_params.frequency = self.control_params.amplitude = 0.0
        self.port_message.registerMessage("control_params",
                                          sawtooth_device_base.ControlParams,
                                          self.control_params_received)