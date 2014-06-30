''' Block 1: sawtooth_control_i.process(), # BLOCK 1 '''
            msg = sawcontrol_base.ControlParams()
            msg.frequency = self.freq
            msg.amplitude = self.amp
            self.port_message.sendMessage(msg)


