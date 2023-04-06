#!/home/richawil/Applications/anaconda3/bin/python

import os
import sys
from infoLog import Log


def main(argv):
    '''
    Log = InfoLog()
    Log.write("This is a test\n")
    Log.write("This is another test\n")
    Log.flush()
    Log.close()

    InfoLog.write("This 2 was a test\n")
    InfoLog.write("This 2 was another test\n")
    InfoLog.flush()
    InfoLog.close()
    '''
    Log.write("This 2 was a test\n")
    Log.write("This 2 was another test\n")
    Log.flush()
    Log.close()
    print("Program Done")
    
if __name__ == '__main__':
    main(sys.argv)
