# Communicates with PyMyo.exe to enable Python support of Myo armband
# Paul Lutz
# Scott Martin
# Fabricate.IO

import time
import subprocess
import sys
import struct
import math

class Myo:
  POSES = {
    0 : "rest",
    1 : "fist",
    2 : "waveIn",
    3 : "waveOut",
    4 : "fingersSpread",
    5 : "reserved1",
    6 : "thumbToPinky",
  }

  CMD = "PyMyo.exe"
  
  PACKET_LEN = 30
  PACKET_FORMAT = "fffffffBB"
  
  def __init__(self):
    pass
  
  def processMyo(self, threadName, delay):
    self.proc = subprocess.Popen(Myo.CMD, bufsize=0, stdout= subprocess.PIPE, stdin= subprocess.PIPE, shell=True)
    self.pose = None
    self.quat = None
    self.accel = None
    
    while True:
      self.last_pose = self.pose
      
      # This will hang until the next data event is read
      newdata = self.proc.stdout.readline().strip()
      
      if len(newdata) != Myo.PACKET_LEN:
        continue
      
      data = struct.unpack(Myo.PACKET_FORMAT,newdata)
      (self.accel, self.quat, self.pose, self.which_arm) = (data[0:3], data[3:7], data[7], data[8])
      
      if (Myo.POSES.get(self.pose) == "fist") and (self.last_pose != self.pose):
        self.proc.stdin.write(chr(1) + "\n")
        self.proc.stdin.flush()
      self.printData()
        
  def calculateEuler(self, quat):
    (w, x, y, z) = quat
    
    if (1 - 2*y*y - 2*z*z !=0):
      roll = math.atan2(2*y*w - 2*x*z, 1 - 2*y*y - 2*z*z)
    else:
      roll = 0
    if (1 - 2*y*y - 2*z*z !=0):
      pitch = math.atan2(2*x*w - 2*y*z, 1 - 2*x*x - 2*z*z)
    else:
      pitch = 0
    
    yaw = math.asin(2*x*y + 2*z*w)
    
    return (roll, pitch, yaw)

  def printData(self):
    arm_str = {
      0: "R",
      1: "L"
    }.get(self.which_arm, "?")
     
    # Rotation is represented by number of stars (as in hello-myo.exe)
    (roll_str, pitch_str, yaw_str) = ["*" * int(r) for r in self.getRotationScaled(18.0)]
   
    pose_str = self.getPoseString()
    
    # Print out the rotation and arm state on the same line each update
    sys.stdout.write('\r[{:17s}][{:17s}][{:17s}][{:1s}][{:15s}]'.format(
        roll_str,
        pitch_str,
        yaw_str,
        arm_str, 
        pose_str
      )
    )
    
  def getAcceleration(self):
    return self.accel
   
  def getRotation(self):
    # Return roll, pitch, and yaw as an array
    return self.calculateEuler(self.quat)
   
  def getRotationScaled(self, scale):
    return [(x+math.pi)/(math.pi*2.0)*scale for x in self.getRotation()]
   
  def getArm(self):
    return self.which_arm
    
  def getPoseString(self):
    return self.POSES.get(self.pose, "unknown")
    
  def getPoseVal(self):
    return self.pose
  