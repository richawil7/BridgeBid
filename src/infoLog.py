'''
Logging Class

This class will be imported by all files and give them access to a 
logging facility.
'''
import os

class Log():
    log_fp = None

    @classmethod
    def open(cls):
        cls.log_fp = open("../logs/info.log", 'w')
        
    @classmethod
    def write(cls, formatStr):
        cls.log_fp.write(formatStr)
        
    @classmethod
    def rotate(cls):
        # Delete the previously saved log file
        os.remove("../logs/save.log")
        # Rename the logging file
        os.rename("../logs/info.log", "../logs/save.log")

    @classmethod
    def flush(cls):
        cls.log_fp.flush()

    @classmethod
    def close(cls):
        cls.log_fp.close()

              
