"""
This module deals with synth point functions.
synth point functions have the signature:
synthPoints(leader,list_of_followers) -> new_tracks

synth point functions are used by add point functions
"""

from ..closure.point import point


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
    def synthFunctor(leader, list_of_followers):
        new_points = []
        new_leader = point(0, leader.allViews())
        for p_old in list_of_followers:
            p = point(0, p_old.allViews())
            results = merge_points_functor(new_leader, p)
            if len(results) > 0:
                new_leader = results[0]
                other_points = results[1:]
                new_points += other_points
            else:  # when len(results)==0
                return new_points
        new_points.append(new_leader)
        return new_points
    return synthFunctor
