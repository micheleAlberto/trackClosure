import sys
import numpy as np
from IPython import embed
from closure.transclosure import transitiveclosure as Partition
from closure.transclosure import save_tracks
from closure.point import point as Track
from closure.point import view as View
from epipolarGeometry import EpipolarGeometry
from fromOpenMVG.wrapper import OpenMVG

def n_connected_components(part,n):
    return [p.id for p in part.points.values() if (len(p.views)==n)]
 
def max_connected_components(part):
    return max(len(p.views) for p in part.points.values() )          
omvg=OpenMVG()
omvg.set_image_dir(sys.argv[1])
omvg.set_feature_dir("./featDir")
matches=omvg.getMatches()
epg=EpipolarGeometry()
for ij in matches:
    pt_i=[]
    pt_j=[]
    for m in matches[ij]:
        pt_i.append(m[1][0:2])
        pt_j.append(m[3][0:2])
    pt_i=np.array(pt_i)
    pt_j=np.array(pt_j)
    epg[ij]=pt_i,pt_j
epg.save('matches.epg')
masterPartition=Partition()
#put matches in , one by one
for ij in matches:
    matchPartition=Partition()
    for m in matches[ij]:
        v0=View(ij[0],m[0],m[1][0],m[1][1])
        v1=View(ij[1],m[2],m[3][0],m[3][1])
        mt=Track(-1,[v0,v1])
        #masterPartition.robust_add_point(p, epg.F, radius=4.0)
        masterPartition.add_point(mt)

save_tracks(masterPartition,'cc.pk')
max_connection=max_connected_components(masterPartition)
for i in range(max_connection-10,max_connection):
    cc_ids=n_connected_components(masterPartition,i)
    if len(cc_ids)<50:
        print i,':',' '.join(map(str,cc_ids))

"""
17 : 140773 144177 150186 150327 151021 151150 151192 151902 152299 152497 152788 152809 152811 153128 153265 153326 153358 153362 153395 153429 153474 153495 153596 153603 153612 153613 153632 153642 153686 153689 153706 153733 153860 153882 153955 153966 153969 153980 153984 153988 153989 154019 154024 154031 154038 154041 154049 154053 154081
19 : 149949 151173 152236 152883 153220 153361 153420 153446 153488 153950 153951 153967 153968 153971 153981 153983 154021 154026 154028 154030
20 : 153179 153001 149375 149656 150845 150998 152110 153083 153234 153334 153347 153430 153431 153476 153906 153924 153948 153959 153965 153977 154036 154045 154076 152190 152744
21 : 148898 150851 153047 153226 153777 153925 153932 153990 153996 154009
22 : 153934 153949 153963 154034

python BenchmarkApp.py --new benchmark.be soft_benchmark
python BenchmarkApp.py --addcc benchmark.be matches.epg cc.pk blablaim/ featDir/  153934 153949 
153963 154034 148898 150851 153047 153226 153777 153925 153932 153990 153996 154009

"""
embed()
    
    


