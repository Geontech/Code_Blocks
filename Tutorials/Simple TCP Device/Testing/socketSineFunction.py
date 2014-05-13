#!/usr/bin/python
"""
Author:  Thomas Goodwin
Company: Geon Technologies
Date:    17 September 2013

Description:
Creates a sine function w/ amplitude from 0.0 -> 1.0 

Command line options are HOST, PORT, and FREQUENCY separated by spaces.

Once running, UP and DOWN can be used to change the output frequency.

Press RIGHT to stop and exit.

Packets are transmitted every 10 ms containing the period of the samples
followed by N samples based on a 100 kHz rate.
"""

""" CURSES """
import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

import curses

""" SINE and TCP socket """
import socket
import sys
import time
import math

"""
Calculates a segment of sinusoid samples covering a certain duration
Base formula: A * sin(2 * pi * F * t + Theta)
   A        Amplitude of sinusoid
   F        Frequency of sinusoid
   Theta    Time offset of sinusoid
   Tnow     Current waveform time
   Fs       Sampling frequency
   Duration Time-length of segment

Returns:
   [Samples] Float-valued samples list

Concept:
                                    Tnow after segment is processed
   Duration -->  v--------------------v
   Samples ---> [-][-][-][-][-][-][-][-][-][-][-][-]
   F / fs ---->  ^--------------------------------^
""" 
def sineSamples(A, F, Theta, Tnow, fs, duration):   
   t = Tnow
   dt = 1.0/fs
   samps = list()
   omega = math.pi * 2.0 * F
   while (t < duration + Tnow):
      val = float(A) * math.sin(omega * t + Theta)
      samps.append(val)
      t += dt
   
   return samps
   
"""
Makes the string packet of [Sample Period, [Samples]]
such that: "p,s1,s2,s3,...,sN"
Each value should be convertible to float or int.
"""
def makeStringPacket(Ts, samples):
   fPacket = [Ts] + samples
   strPacket = ""
   for f in fPacket:
      strPacket += str("%f," % f)
   strPacket = strPacket[:-1]
   return strPacket
   
   
""" 
Main Body
"""
txPeriod = 0.025
fs = 10000.0
fStep = 100.0 # Hz
# Command line argument 1 is the IP of the server
# Command line argument 2 is the PORT of the server
# Command line argument 3 is the starting FREQUENCY of the sinusoid.
if (1 == len(sys.argv)):
   HOST = '127.0.0.1'
   PORT = 9999
   freq = 500.0
else:
   HOST, PORT = sys.argv[1], int(sys.argv[2], base=10)
   freq =  abs(float(sys.argv[3]))
   fs = 8.0 * freq
   fStep = fs / 10.0

try:
   stdscr = curses.initscr()
   curses.noecho()
   curses.cbreak()
   stdscr.nodelay(True)
   stdscr.keypad(True)
   
   sock = None
   updateScreen = True
   i = 0
   exitLoop = False  
   
   stdscr.addstr(0,0,"Increase/Decrease frequency use UP or DOWN arrows")
   stdscr.addstr(1,0,"Exit use RIGHT arrow")
   tstart = time.time()
   while True:
      # Calculate new samples and packet
      tNow = time.time()
      samps = sineSamples(1.0, freq, 0.0, tNow, fs, txPeriod)
      pkt = makeStringPacket(1.0/fs, samps)
      
      # Wait for time to expire and get user input
      while (time.time() < tNow + txPeriod):
         # screen output     
         c = stdscr.getch()   
         if (c == curses.KEY_UP):
            updateScreen = True
            freq += fStep
            if freq > fs / 2.0:
                freq = fs
         elif (c == curses.KEY_DOWN):
            updateScreen = True
            freq -= fStep
            if 0 >= freq:
                freq = fStep
         elif ((c == curses.KEY_RIGHT) or (30.0 < tNow - tstart)):
            stdscr.addstr(3,0,"Exiting...\n")
            exitLoop = True
            break;
            
         if (updateScreen):
            stdscr.addstr(2,0,"Running at:     {0:6.2f} Hz ({1:d} samples)\t\t".format(freq, len(samps)))
            updateScreen = False
         
      
      # Transmit and close socket
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect((HOST, PORT))
      sock.sendall(pkt)
      sock.close()
      
      # Exit?
      if (True == exitLoop):
         break;
      
finally:
   stdscr.keypad(0)
   stdscr.nodelay(False)
   curses.nocbreak()
   curses.echo()
   curses.endwin()
   
   if (None != sock):
      sock.close()
      
   print "Finished.  Press ENTER to exit."
   raw_input()