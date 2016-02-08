import sys
import os
import numpy as np
from IPython import embed

from ..src.closure.transclosure import transitiveclosure as Partition
from ..src.closure.transclosure import save_tracks
from ..src.closure.point import point as Track
from ..src.closure.view import view as View
from ..src.geometry.epipolarGeometry import EpipolarGeometry
from ..src.fromOpenMVG.wrapper import OpenMVG
from ..src.roamfree.roamfreeIO import write_rf_tracks # (image_names,tracks,filename)
from ..src.roamfree.roamfreeIO import  write_rf_viewTimestamp # (image_names,filename)
from ..src.roamfree.roamfreeIO import  write_rf_view_stats # (self,tracks,filename='views.csv')

def n_connected_components(part,n):
    return [p.id for p in part.points.values() if (len(p.views)==n)]

def max_connected_components(part):
    return max(len(p.views) for p in part.points.values() )




from ..src.functionalClosure.mergeF import make_merge_with_validation #(radius, gEpG)
from ..src.functionalClosure.mergeF import hard_merge # (p, q)
#from ..src.functionalClosure.mergeF import make_merge_interactive 
# (merge_functor, outcome_filter,oracle_partition, gEpG, outcome_functor=None)
from ..src.functionalClosure.synthF import make_synthPoints # (merge_points_functor)
from ..src.functionalClosure.addPointF import make_add_point # (SynthPoints_functor)
from ..src.functionalClosure.closureF import make_closure # (add_pt_functor)

def make_my_addpoint():
    synth = make_synthPoints(hard_merge)
    add_point = make_add_point(synth)
    return add_point

def make_smart_add_point(gEpG,radius):
    merge = make_merge_with_validation(radius, gEpG)
    synth = make_synthPoints(merge)
    add_point = make_add_point(synth)
    return add_point

def store_partition(cc_dir,part):
    _cc_dir='data/'+cc_dir
    os.mkdir(_cc_dir)
    save_tracks(part,_cc_dir+'cc.pk')
    write_rf_tracks(omvg.image_id2name,part, _cc_dir+'cc.txt')
    write_rf_viewTimestamp(omvg.image_id2name, _cc_dir+'timestamps.txt')
    write_rf_view_stats(tracks,filename= _cc_dir+'views.txt')
    return 

def close(add_point_functor):
    connected_compoenents=Partition()
    for ij in matches:
        for m in matches[ij]:
            v0=View(ij[0],m[0],m[1][0],m[1][1])
            v1=View(ij[1],m[2],m[3][0],m[3][1])
            mt=Track(-1,[v0,v1])
            add_point_functor(connected_compoenents,mt)
    return connected_compoenents




def main(argv):
    assert(len(argv)==3 )
    datadir=sys.argv[1]
    image_dir=sys.argv[2]
    omvg=OpenMVG()
    omvg.set_feature_dir(datadir)
    omvg.set_image_dir(image_dir)
    omvg.loadImageMap()
    matches=omvg.getMatches()
    print 'matches read from openMVG'
    epg=EpipolarGeometry()
    for ij in matches:
        pt_i=[]
        pt_j=[]
        print ij,": ",len (matches[ij])," ",
        for m in matches[ij]:
            pt_i.append(m[1][0:2])
            pt_j.append(m[3][0:2])
        pt_i=np.array(pt_i)
        pt_j=np.array(pt_j)
        epg[ij]=pt_i,pt_j
        print "F"
    epg.save(datadir+"/matches.epg")
    
    def make_my_addpoint():
        synth = make_synthPoints(hard_merge)
        add_point = make_add_point(synth)
        return add_point
    def make_smart_add_point(gEpG,radius):
        merge = make_merge_with_validation(radius, gEpG)
        synth = make_synthPoints(merge)
        add_point = make_add_point(synth)
        return add_point

    def store_partition(cc_dir,part):
        _cc_dir=datadir+'/'+cc_dir
        os.mkdir(_cc_dir)
        save_tracks(part,_cc_dir+'cc.pk')
        write_rf_tracks(omvg.image_id2name,part, _cc_dir+'cc.txt')
        write_rf_viewTimestamp(omvg.image_id2name, _cc_dir+'timestamps.txt')
        write_rf_view_stats(part,omvg.image_id2name,filename= _cc_dir+'views.txt')
        return 

    def close(add_point_functor):
        connected_compoenents=Partition()
        for ij in matches:
            for m in matches[ij]:
                v0=View(ij[0],m[0],m[1][0],m[1][1])
                v1=View(ij[1],m[2],m[3][0],m[3][1])
                mt=Track(-1,[v0,v1])
                add_point_functor(connected_compoenents,mt)
        return connected_compoenents
    connected_compoenents=close(make_my_addpoint())
    store_partition('cc/',connected_compoenents)
    smart_components=close(make_smart_add_point(epg,10.))
    store_partition('smc/',smart_components)
    max_connection=max_connected_components(connected_compoenents)
    for i in range(max_connection-10,max_connection):
        cc_ids=n_connected_components(connected_compoenents,i)
        if len(cc_ids)<50:
            print i,':',' '.join(map(str,cc_ids))


if __name__ == "__main__":
    main(sys.argv)


