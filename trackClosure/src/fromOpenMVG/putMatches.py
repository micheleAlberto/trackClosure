from trackCentroid import linear_centroid as centroid

def partitionToChainOfViews(partition, centroid_functor,limiter=None):
    chains = []
    track_ids=select_track_ids(partition,limiter)
    for t_id in partition.points.keys():
        T = partition.points[t_id]
        chain = []
        for im_id in sorted(T.views.keys()):
            best_keypoint = centroid_functor(T.views[im_id])
            chain.append( best_keypoint.key() )
        chains.append(chain)
    return chains

def ChainOfViewsToChainOfMatches(chains):
    matches = {}
    for ch in chains:
        for i in range(len(ch)-1):
            kp_I,kp_J = ch[i:i+2]
            im_pair = (kp_I[0], kp_J[0])
            #I,J = im_pair
            if im_pair in matches:
                matches[im_pair].append( (kp_I[1], kp_J[1]))
            else:
                matches[im_pair] = [(kp_I[1], kp_J[1])]
    return matches

def writeOpenMVGMatches(matches,write_functor):
    for M in matches:
        pair_header="{} {}\n".format(M[0],M[1])
        lenght="{}\n".format(len(matches[M]))
        body=""
        for m in matches[M]:
            body+="{} {}\n".format(m[0],m[1])
        match_block=pair_header+lenght+body
        write_functor(match_block)
    return

def writeOpenMVGMatchesFile(matches,file_name):
    with open(file_name,'w') as fout:
         wr_f=lambda x:fout.write(x)
         writeOpenMVGMatches(matches,wr_f)

def exportPartition(partition,file_name,limiter=None):
    chains=partitionToChainOfViews(partition, centroid,limiter)
    matches=ChainOfViewsToChainOfMatches(chains)
    writeOpenMVGMatchesFile(matches,file_name)

class TrackLimiter:
    def __init__(self,upper_limit,track_cost_functor):
        self._cost_functor=track_cost_functor
        self._l=upper_limit
        self._c=0
    def check(self,track):
        if (self._l<=self._c):  
            return False
        else:
            track_cost=self._cost_functor(track)
            if (self._l<=(self._c+track_cost)) :
                self._c+=track_cost
                return True
            else :
                return False

def kpLimit(max_keypoint):
    return TrackLimiter(max_keypoint,lambda t:len(t.views))

def trackLimit(max_track):
    return TrackLimiter(max_track,lambda t:1)

def select_track_ids(part,limiter):
    if limiter:
        track_list=sorted(part.points.values() , key= lambda t:-len(t.views))
        selected_track_ids=[t.id for t in track_list if limiter.check(t)]
        return selected_track_ids
    else: return part.points.keys()

