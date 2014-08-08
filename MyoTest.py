from myo import Myo
from threading import Thread
from getpass import getpass



def main():
  myMyo = Myo()
  startThread(myMyo)
 
def startThread(tempMyo):
  t = Thread(target=tempMyo.processMyo, args=("Thread-1",2,))
  t.daemon = True
  t.start()
  while True:
    pass
      
if __name__ == "__main__":
    main()