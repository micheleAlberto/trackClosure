import numpy as np
def stringToIntTuple(line):
    return tuple(int(s) for s in line.split() if s.isdigit())

def getMatchLines(match_file_name):
    with open(match_file_name) as fin:
        LL=fin.readlines()
        LL.reverse()
    return LL

def readMatch(LL,reg):
    header1=stringToIntTuple(LL.pop())
    assert len(header1)==2
    header2=int(LL.pop())
    match_list=np.zeros((header2,2),np.int)
    for i in range(header2):
        match=stringToIntTuple(LL.pop())
        match_list[i,0]=match[0]
        match_list[i,1]=match[1]
    reg[header1]=match_list

def parseMatches(match_file_name):
    R=dict()
    ll=getMatchLines(match_file_name)
    while len(ll)>1:
        readMatch(ll,R)
    return R

#TESTING:
def main():
    R=dict()
    ll=getMatchLines('matchDir/matches.f.txt')
    while len(ll)>1:
        readMatch(ll,R)
    for m in R:
        print m[0],"/",m[1]," :\t",len(R[m])
        #print len(R[m])
if __name__ == "__main__":
    main()
