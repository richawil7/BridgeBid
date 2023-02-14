#!/home/richawil/Applications/anaconda3/bin/python

import os
import sys
from teamState import TeamState


def main(argv):
    #openRegistry = OpenerRegistry()
    teamState = TeamState()
    teamState.show()
    bidList = []
    teamState.fetchTeamState(bidList)
    teamState.show()

    print("Program Done")
    
if __name__ == '__main__':
    main(sys.argv)
