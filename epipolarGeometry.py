
import numpy as np
import cv2 
from exceptions import TypeError,KeyError
from random import uniform
from random import choice
import sys
import pickle

def treeType(x):
    t=type(x)
    if t == np.ndarray:
        return "ndarray<{}>[{}]".format(x.dtype,','.join(map(str,x.shape)))
    if t in [int,float,str]:
        return t.__name__
    if t in [tuple,list]:
        return "{}<{}>".format(t.__name__,', '.join([treeType(y) for y in x]))
    if t == dict :
        return "dict <{}>-> <{}>".format(treeType(x.keys()[0]),treeType(x.values()[0]))
    return t.__name__
    
def indexSwap(couple):
    return (couple[1],couple[0])

def isNormal(ij):
    return (ij[0]<ij[1])

def normalize(ij,F):
    if isNormal(ij):
        return (ij,F)
    else :
        return ((ij[1],ij[0]),F.transpose().copy())
def normalizeij(ij):
    if isNormal(ij):
        return ij
    else:
        return (ij[1],ij[0])

class EpipolarGeometry:
    def __init__(self,**kw):
        self.F=dict();
        self.N=dict();
        #!convenzione :
        #ij in F => i<j  => ij[0]<ij[1]
        for k in kw:
            self[k]=kw[k]
    def __iter__():
        return self.F.__iter__()
    def set_pair_by_match_points(self,pair_a_b,points_a,points_b):
        print "!",
        f, mask=cv2.findFundamentalMat(points_a, points_b )
        positive_count=sum(mask)
        ij,f=normalize(pair_a_b,f)
        self.F[ij]=f
        self.N[ij]=positive_count
    def set_pair_by_fundamentalMatrix(self,pair_a_b,f_a_b,n):
        ij,f=normalize(pair_a_b,f_a_b)
        self.F[ij]=f
        self.N[ij]=n
    def f(self,key):
        if isNormal(key):
            return self.F[key]
        else:
            return self.F[normalizeij(key)].transpose().copy()
    def n(key):
        return self.N[normalizeij(key)]

    def __setitem__(self, key, item):
        if not (
            type(key)==tuple and 
            len(key)==2 and
            type(key[0])==int and
            type(key[1])==int ):
            raise TypeError("key should be a pair of int")
        if not (
            type(item)==tuple and 
            len(item)==2):
            raise TypeError("value should be a tuple containing a numpy fundamental matrix and an int or a pair of vector of keypoints")
        if (
                (type(item[0])==np.ndarray)
            and (type(item[0])==type(item[1]))
            and (item[0].shape==item[1].shape)):
            return self.set_pair_by_match_points(key,item[0],item[1])
        if (
            (type(item[0])==np.ndarray)
            and (item[0].shape==(3,3))):
            return self.set_pair_by_fundamentalMatrix(key,item[0],int(item[1]))
        print "KEY:",treeType(key)
        print "ITEM:",treeType(item)
        assert(False)
    def __getitem__(self, key): 
        return self.f(key)
    def __len__(self): 
        return len(self.F)
    def __delitem__(self, key):
        del self.F[normalizeij(key)]
        del self.N[normalizeij(key)]
    def has_key(self, key):
        normalized=normalizeij(key)
        return self.F.has_key(normalizeij(key))
    def keys(self):
        return self.F.keys()
    def values(self):
        return self.F.values()
    def __iter__(self):
        return self.F.iterkeys()
    def __contains__(self,item):
        return self.has_key(item)
    def items(self):
        return self.__dict__.items()
    @staticmethod
    def load(filename):
        if not '.epg' in filename:
            _filename=filename+'.epg'
        else:
            _filename=filename
        with open(_filename) as fin:
            B=pickle.load(fin)
        return B
    def save(self,filename):
        if not '.epg' in filename:
            _filename=filename+'.epg'
        else:
            _filename=filename
        with open(_filename,'w') as fo:
            pickle.dump(self,fo)
        return
def randKey():
    return (int(uniform(0,100)),int(uniform(0,100)))

def randF():
    return np.random.normal(0,1,(3,3))

def randN():
    return uniform(100,200)
def main(argv):
    dd={randKey():(randF(),randN()) for i in range(100)}
    e=EpipolarGeometry()
    for k in dd:
        print "add ",k,":",len(e)#,dd[k]
        e[k]=dd[k]
    print e.keys()
    for k in dd:
        print k," in e"
        assert k in e
    for k in dd:
        print k," in e"
        assert (k[1],k[0]) in e
    for k in e:
        print k," in dd"
        assert (k in dd or ((k[1],k[0]) in dd))


def validation(gEpG,tracks):
    X={ (i,j): validation_epg(i,j,gEpG[(i,j)],tracks) for i,j in gEpG}
    return { foo:bar for foo,bar in X.iteritems() if bar is not None}
        


def validation_epg(i,j,Fij,tracks):
    point_id_set=set(tracks.views[i].values())
    point_id_set.intersection_update(tracks.views[j].values())
    if len(point_id_set)==0:
        return None
    return np.average([error(i,j,Fij,tracks.points[p_id]) for p_id in point_id_set])
    
    
def error(i,j,Fij,p):
    hi=choice(p.views[i]).hpt()
    hj=choice(p.views[j]).hpt()
    Ferr=np.dot(hi ,np.dot( Fij , hj.T ))
    Ferr=np.abs(Ferr)
    Ferr=1-np.exp(-Ferr)
    return Ferr
    
def plot(validation_dict):
    m=max( max( i,j) for i,j in validation_dict)+1
    P=np.zeros((m,m))
    for i,j in validation_dict:
        P[i,j]=validation_dict[i,j]
        P[j,i]=validation_dict[i,j]
    return P

if __name__ == "__main__":
    argv=sys.argv
    main(argv)
