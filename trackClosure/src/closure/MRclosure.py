import pickle
from pytable.closure import transclosure
from pytable.closure.transclosure import robust_closure
from pytable.settings import paths
from Queue import Queue 
import gc
from itertools import tee , imap
from IPython.parallel import CompositeError


R=32.
def my_reduction(x,y):
    assert not (y is  None), "! robust_reduction : second argument is None"
    assert not (x is  None), "! robust_reduction : first argument is None"
    print '[new_reduction]\t{} + {}'.format(x.views.keys(),y.views.keys())
    if orchestra:
        x.robust_closure(y,orchestra.gEpG,radius=16.)
    else:
        x.robust_closure(y,remote_gEpG,radius=16.)
    print '[new_reduction]\t = {}'.format(x.views.keys() )
    return x


def close_in_memory(mbins,trc=transclosure.transitiveclosure(),lbv=None,reduction=my_reduction,matchLabel=None,gEpG=None):
    assert(gEpG)
    def pre_args(m):
        matches=m.mread(matchLabel)
        Ii,Ij=m.Ii,m.Ij,
        kp_i=m.I().kpread()
        kp_j=m.J().kpread()
        return matches,Ii,Ij,kp_i,kp_j,gEpG[Ii,Ij]
    my_imap=lbv.imap if lbv else imap
    if lbv and gEpG:
         lbv.client[:].push(dict(gEpG=gEpG))
    argList = imap(pre_args,mbins)
    tracks_list=list(my_imap(transclosure.matches2tracks,argList))
    while len(tracks_list)>1:
        print "close_random ",len(tracks_list)
        if len(tracks_list)%2==1:
            tracks_list.append(transclosure.transitiveclosure())
            #print "poppint one empty element len=",len(tracks_list)
        tracks_list=sort_tracks_lists(tracks_list)
        left_track_list=[tr for _n,tr in enumerate(tracks_list) if _n%2==0]
        right_track_list=[tr for _n,tr in enumerate(tracks_list) if _n%2==1]
        try:
            tracks_list_out=my_imap(reduction,left_track_list,right_track_list)
            tracks_list=list(tracks_list_out)
        except CompositeError, e:
            e.raise_exception()
    return tracks_list[0]


def diff(e1,e2):
    S1=set(e1.views.keys())
    S2=set(e2.views.keys())
    union=len(S1.union(S2))
    intersection=len(S1.intersection(S2))
    return union-intersection

def select(e,used,in_list):
    candidates=[ei for ei in range(len(in_list)) if not ei in used]
    return min (candidates , key=lambda x: diff(in_list[x],in_list[e]))
              
def sort_tracks_lists(in_list):
    used=set()
    ei=0
    out_list_index=[]  
    while len(out_list_index)<len(in_list):
        ei=select(ei,used,in_list)
        out_list_index.append(ei)
        used.add(ei)
    return [in_list[i] for i in out_list_index]

class MatchBucket:
    def __init__(self,m,label=None):
        self.I=set([m.Ii,m.Ij])
        self.matches=[m]
        self.label=label
        self.n=m.n(label)
    def add(self,m):
        self.I.add(m.Ii)
        self.I.add(m.Ij)
        self.n+=m.n(self.label)
        self.matches.append(m)
    def likelihood(self,m):
        f=0
        if m.Ii in self.I:
            f+=1
        if m.Ij in self.I:
            f+=1
        return float(f*m.n())/self.n

def close_on_disk(mbins,lbv=None,reduction=my_reduction,matchLabel=None,gEpG=None):
    my_imap=lbv.imap if lbv else imap
    if lbv and gEpG:
         lbv.client[:].push(dict(remote_gEpG=gEpG))
    num_bins=len(mbins)
    num_buckets=num_bins/128
    buckets=[]
    q=Queue()
    paths.ensureDir(paths.pointDir)
    for i,m in enumerate(mbins):
        if i<num_buckets:
            b=MatchBucket(m,matchLabel)
            buckets.append(b)
        else :
            q.put(m)
    while not q.empty():
        m=q.get()
        likelihoods={b:b.likelihood(m) for b in buckets}
        if sum(likelihoods.values())==0:
            q.put(m)
        else:
            b=max(likelihoods,key=likelihoods.get)
            b.add(m)
    for bi,b in enumerate(buckets):
        filename=paths.pointDir+'bucketlist{}.txt'.format(bi)
        with open(filename,'w') as fp:
            line=','.join(map(str,sorted(b.I)))+'\n'
            print "bucket #{}, {} matches".format(bi,b.n)
            print line
            fp.write(line)
            for m in b.matches:
                line='{},{},{}\n'.format(m.Ii,m.Ij,m.n())
                fp.write(line)
    partial_track_files=[]
    for bi,b in enumerate(buckets):
        gc.collect()
        with open(filename,'w') as fo:
            mbins_in_the_bucket=b.matches
            partial_tracks=close_random(mbins_in_the_bucket,lbv=lbv,reduction=reduction,matchLabel=matchLabel,gEpG=gEpG)
            filename=paths.pointDir+'tracksPartial{}.txt'.format(bi)
            pickle.dump(partial_tracks,fo)
            partial_track_files.append(filename)
            del partial_tracks
    print "Tracking : Second phase"
    return partial_track_files

def wrap_closure(partial_track_files,lbv=None,reduction=my_reduction,gEpG=None) :
    def load_tracks(filename):
        with open(filename) as fin:
             tracks=pickle.load(fin)
        return tracks
    my_imap=lbv.imap if lbv else imap
    if lbv and gEpG:
         lbv.client[:].push(dict(remote_gEpG=gEpG))
    tracks_list=map(load_tracks,partial_track_files)
    while len(tracks_list)>1:
        print "close_random ",len(tracks_list)
        if len(tracks_list)%2==1:
            tracks_list.append(transclosure.transitiveclosure())
            print "poppint one empty element len=",len(tracks_list)
        print "sorting list:"
        for ti,t in enumerate(tracks_list):
            print ti,t.views.keys()
        tracks_list=sort_tracks_lists(tracks_list)
        print "sorted list:"
        for ti,t in enumerate(tracks_list):
            print ti,t.views.keys()
        left_track_list=[tr for _n,tr in enumerate(tracks_list) if _n%2==0]
        right_track_list=[tr for _n,tr in enumerate(tracks_list) if _n%2==1]
        try:
            tracks_list_out=my_imap(reduction,left_track_list,right_track_list)
            tracks_list=list(tracks_list_out)
        except CompositeError, e:
            e.raise_exception()
    return tracks_list[0]
