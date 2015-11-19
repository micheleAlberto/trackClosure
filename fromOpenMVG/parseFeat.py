import numpy as np
import sys
def stringToFloatTuple(line):
    return tuple(float(s) for s in line.split())


def getFeatLines(feat_file_name):
    with open(feat_file_name) as fin:
        LL=fin.readlines()
    return LL

def parseFeat(feat_file_name):
    ll=getFeatLines(feat_file_name)
    keypointBuffer=np.zeros((len(ll),4),np.float)
    for li,l in enumerate(ll):
        xyso=stringToFloatTuple(l)
        keypointBuffer[li]=xyso
    return keypointBuffer

#TESTING:
def main():
    argv=sys.argv
    if len(argv)==1:
        print parseFeat('matchDir/P1220953.feat')
    else:
        print parseFeat(argv[1])
if __name__ == "__main__":
    main()
