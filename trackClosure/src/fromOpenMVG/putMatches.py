import trackCentroid.linear_centroid as centroid

def partitionToChainOfViews(partition, centroid_functor):
    chains = []
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

def exportPartition(partition,file_name):
    chains=partitionToChainOfViews(partition, centroid)
    matches=ChainOfViewsToChainOfMatches(CoV)
    writeOpenMVGMatchesFile(matches,file_name)
