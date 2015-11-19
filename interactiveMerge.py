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
            #may use Counter instead of Set?
            xO=set(soft_fetch(oracle,track_x))
            yO=set(soft_fetch(oracle,track_y))
            """
            Errors in the xO/yO track operand
            if len(_O)==0 we don' t kow much about the track because supervised 
                information is not available
            if len(_O)==1 track_y is a correct track as far as we know !!!
            if len(_O)>1  track_y is already wrong before the computation !!!
            """
            ZO=[set(fetch(oracle,track_z_it)) for track_z_it in tracks_z]
            """
            Errors in the results Z:
            tracks_z and ZO may contain 0,1 or 2 elements
                0:if the computation discarded both points (should it happen? maybe, maybe not, probably should be a rare event)
                1:if the computation merged the tracks
                2:if the computation splitted the tracks
            for zO in ZO:
                if len(zO)==0 we don' t kow much about the track because supervised 
                information is not available
                if len(zO)==1 the resulting track is correct as far as we know
                if len(zO)>1 the resulting track is wrong
            """
            correct_operands=(len(xO)<2 and len(yO)<2)
            mutually_correct_operands=(len(xO.union(yO))<2)
            known_correct_operands=(len(xO)==1 and len(yO)==1)
            known_mutually_correct_operands=(len(xO.union(yO))==1)
            correct_results=all( len(zO)<2 for zO in ZO)
            known_correct_results=all( len(zO)==1 for zO in ZO)
            correct_operation=correct_results if correct_operands else True
            known_correct_operation=known_correct_results if correct_operands else True
            recover= correct_results and not correct_operands
            known_recover= known_correct_results and not correct_operands
            """completeness:
            missing keypoints:
            keypoints that 
                are in the operands
                are not in the results
            spilled keypoints:
            missing keypoints that
                should be in the results
                have the same oracle of some result
            """
            operand_kp=set([v.key() for v in track_x.allViews()+track_y.allViews()])
            result_kp=reduce(
                lambda a,b:a+b,
                [[v.key() for v in track_z ] for track_z in tracks_Z]
                [])
            result_kp=set(result_kp)
            missing = operand_kp.difference(result_kp)
            missing_oracles=[]
            for kp in missing:
                if kp[0] in oracle_partition.views:
                    if kp[1] in oracle_partition.views[kp[0]]:
                        missing_oracles.append(
                            oracle_partition.views[kp[0]])
            dominant_oracles_of_results=set([dominant(zO) for zO in ZO])
            spilled_oracles=Counter([o 
                for o in missing_oracles
                if o in dominant_oracles_of_results])
            complete_operation=len(spilled_oracles)==0
            spilled=sum(spilled_oracles.values())
            condition_to_interrupt=(
                (interrupt_if_not_correct   and not correct_operation)
            or  (interrupt_if_not_complete  and not complete_operation)
            )
            if condition_to_interrupt:
                s=get_report(track_x,track_y,result)
                print s
                print 'correct_operands: ',correct_operands
                print 'mutually_correct_operands: ',mutually_correct_operands
                print 'known_correct_operands: ',known_correct_operands
                print 'known_mutually_correct_operands: ',known_mutually_correct_operands
                print 'correct_results: ',correct_results
                print 'known_correct_results: ',known_correct_results
                print 'correct_operation: ',correct_operation
                print 'recover: ',recover
                print 'known_recover: 'known_recover
                print 'oracles of X:',xO
                print 'oracles of Y:',yO
                print 'dominant oracles in results:',dominant_oracles_of_results
                print ('spilled oracles:',
                    ', '.join(['{}:{}'.format(oi[0],oi[1]) 
                                for oi in spilled_oracles.iteritems()]))
                print ('dominant of resu:',
                    ', '.join(['{}:{}'.format(oi[0],oi[1]) 
                                for oi in spilled_oracles.iteritems()]))
                embed()
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


