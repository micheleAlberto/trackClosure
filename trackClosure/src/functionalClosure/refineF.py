from mergeF import make_merge_with_validation # (radius,gEpG)
from synthF import make_synthPoints # (merge_points_functor)    
from addPointF import make_add_point # (SynthPoints_functor)
from closureBenchmark.closureBenchmark import all_edges # (cc,gEpG)
from ..closure.transclosure import transitiveclosure as Partition
from ..closure.point import point as Track
from random import shuffle, choice
from tqdm import tqdm
def make_refine_connected_component(gEpG,radius):
    smart_merge = make_merge_with_validation(radius,gEpG)
    synth = make_synthPoints(smart_merge)
    add_point = make_add_point(synth) 
    def refiner(cc):        
        part = Partition()
        E=list(all_edges(cc,gEpG))
        shuffle(E)
        for e in tqdm(E):
            t=Track(0,e)
            add_point(part,t)
        return part.points.values()
    return refiner




    
