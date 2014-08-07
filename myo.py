import time
from threading import Thread
import os
import subprocess
import sys
import struct
import math
from getpass import getpass

class Myo:
  def __init__(self):
    self.poses = {0 : "rest",
                1 : "fist",
                2 : "waveIn",
                3 : "waveOut",
                4 : "fingersSpread",
                5 : "reserved1",
                6 : "thumbToPinky",
                7 : "unknown",
                255 : "unknown",
    }
  
  def processMyo(self, threadName, delay):
    cmd = "PyMyo.exe"
    self.proc = subprocess.Popen(cmd, bufsize=0, stdout= subprocess.PIPE, stdin= subprocess.PIPE, shell=True)
    self.pose = 255
    while True:
      newdata = self.proc.stdout.readline().strip()
      if len(newdata) == 30:
        my_struct = struct.unpack("fffffffBB",newdata)
        self.calculateEuler(my_struct[3],my_struct[4],my_struct[5],my_struct[6])
        self.whichArm = my_struct[8]
        self.lastpose = self.pose
        self.pose = my_struct[7]
        if (self.poses[self.pose] == "fist") and (self.poses[self.lastpose] != "fist"):
          self.proc.stdin.write(chr(1) + "\n")
          self.proc.stdin.flush()
        self.printData()
        #print self.pose
        #print my_struct[8]
        '''
        for x in my_struct:
          print x
        '''
  def calculateEuler(self, w, x, y, z):
    self.roll = math.atan2(2*y*w - 2*x*z, 1 - 2*y*y - 2*z*z)
    self.pitch = math.atan2(2*x*w - 2*y*z, 1 - 2*x*x - 2*z*z)
    self.yaw = math.asin(2*x*y + 2*z*w)
    
    myPi = math.pi
    self.roll_w = int(((self.roll +myPi)/(myPi*2.0))*18.0)
    self.pitch_w = int(((self.pitch +myPi)/(myPi*2.0))*18.0)
    self.yaw_w = int(((self.yaw +myPi)/(myPi*2.0))*18.0)
    '''
    self.roll_w = int((self.roll + myPi/2.0)/(myPi*18.0)
    self.pitch_w = int((self.pitch + myPi/2.0)/myPi*18.0)
    self.yaw_w = int((self.yaw + myPi/2.0)/myPi*18.0)
    '''
    
  def startThread(self):
    t = Thread(target=self.processMyo, args=("Thread-1",2,))
    t.daemon = True
    t.start()
    while True:
      self.input = getpass("")
      sys.stdout.write("\033[5m")
      
      
      
    
    
  
  def printData(self):
  
    sys.stdout.write("\r")
        
  #print roll
    sys.stdout.write("[")
    for x in range(0, 17):
      if self.roll_w >= x:
        sys.stdout.write("*")
      else:
        sys.stdout.write(" ")
    sys.stdout.write("]")
    
    #print pitch
    sys.stdout.write("[")
    for x in range(0, 17):
      if self.pitch_w >= x:
        sys.stdout.write("*")
      else:
        sys.stdout.write(" ")
    sys.stdout.write("]")
    
    #print yaw
    sys.stdout.write("[")
    for x in range(0, 17):
      if self.roll_w >= x:
        sys.stdout.write("*")
      else:
        sys.stdout.write(" ")
    sys.stdout.write("]")
    
    #print arm
    sys.stdout.write("[")
    if self.whichArm == 0:
      sys.stdout.write("R")
    elif self.whichArm == 1:
      sys.stdout.write("L")
    else:
      sys.stdout.write("?")
    sys.stdout.write("]")
    
    sys.stdout.write("[")
    count = 0
    for x in self.poses[self.pose]:
      count += 1
      sys.stdout.write(x)
    for x in range(0, 15-count):
      sys.stdout.write(" ")
      
    sys.stdout.write("]")
    
    
    