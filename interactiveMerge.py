from closure.validation.noValidation import noValidation
from closure.validation import validation
from closure.validation.compactRepresentation import compactPoint

from partitionTransfer import soft_fetch, 
from partitionTransfer import soft_partition_transfer
from partitionTransfer import track_is_wrong
from partitionTransfer import dominant
from collections import Counter
from printOperation import make_print_operation

def print_pair_of_tracks(track_x,track_y):
    sep='\t\t'
    s=""
    images=set(track_x.views.keys()+track_y.views.keys())
    s+=sep.join(['Im','P','Q'])
    for im_id in sorted(images):
        line=[im_id,
              soft_fetch_views(oracle,track_x.views[im_id]),
              soft_fetch_views(oracle,track_y.views[im_id])]
        s+=sep.join(map(str,line))
    return s


"""
#Merge Functions
functions that provide functions that implement the merging of two tracks
    merge: (trackA,trackB)->result_tracks
"""
def make_merge_with_validation(radius,gEpG):
    """
    provide an implementation of a merge function usign multiview validation    
    (float) radius is the threshold of the validation filter
    gEpG={(i,j):Fij}  is a dictionary that maps pair of images (by index) to 
        fundamental matrices
    return a merge function
        robust_merge: (trackA,trackB)->result_tracks
    """
    def foo(trackA,trackB):
        validation_report=validation(trackA,trackB,gEpG,radius)
        if validation_report.merge:
            new_leader=merge(validation_report,new_leader,p,radius=radius,permissiveLimit=4)
            return [new_leader]
        else:
            new_leader,q=split(validation_report,new_leader,p)
            return [new_leader,q]
    return foo



def make_merge_interactive(
        merge_functor,
        outcome_filter,
        oracle_partition,
        interrupt_if_not_correct=True,
        interrupt_if_not_complete=True):
    """
    provide an interactive implementation of the given merge operator
    both input and output are merge functions in the form
        merge_functor:(trackA,trackB)->result_tracks
    """ 
    get_report=make_print_operation(gEpG,oracle)
        def foo(track_x,track_y):
            tracks_Z=merge_functor(track_x,track_y)
            outcome=MergeOutcome(track_x,track_y,tracks_Z,gEpG,oracle)
            if outcome_filter(outcome):
                raise outcome
    return foo 
       

"""
#Synth point functions 
synthPoints(leader,list_of_followers) -> new_tracks
"""
def make_synthPoints(merge_points_functor):
    """
    provide an implementation of synth points using merge_points_functor as a 
    merge operation.
        merge_points_functor(trackA,trackB) -> new_tracks
    where new_tracks is a list of at most 2 tracks
    Return a synthPoints function:
        synthPoints(leader,list_of_followers) -> new_tracks
    examples:
    make_synthPoints(hard_merge)
    make_synthPoints(merge_with_validation)
    """
    def foo(leader,list_of_followers):
        new_points=[]
        new_leader=point(0,leader.allViews())
        for p_old in list_of_followers:
            p=point(0,p_old.allViews())
            results=merge_points_functor(new_leader,p)
            if len(results)>0:
                new_leader=results[0]
                other_points=results[1:]
                new_points+=other_points
            else:#when len(results)==0
                return new_points
        new_points.append(new_leader)
        return new_points
    return foo    


