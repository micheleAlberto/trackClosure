"""
This module deals with merge functions.
Merge functions have the signature:
merge(track1,track2)->track3

track3 should have id=0 to be inserted in a partition

merge functions are used by synth functions
"""
from collections import Counter
import numpy as np
from ..closure.point import point
from ..closure.validation.transclosureMergeValidation import validation
#has signature: validation(Point_P, Point_Q, gEpG,radius,a)
from mergeBenchmark.printOperation import make_print_operation
from mergeBenchmark.MergeOutcome import MergeOutcome


def hard_merge(p, q):
    PuQ = point(0, [])  # resulting point
    inserted = set()
    for v in (p.allViews() + q.allViews()):
        if not v.key() in inserted:
            inserted.add(v.key())
            PuQ.add_view(v)
    return [PuQ]


def informed_merge(vr, p, q, radius=4.):
    """
    Use a validation report to merge 2 points
    Only keypoints not further than radius then theyr expectation are merged
    """
    PuQ = point(0, [])
    inserted = set()
    for im_id in vr.R:
        if im_id in p.views:
            for v in p.views[im_id]:
                key = v.key()
                dist = np.linalg.norm(vr.R[im_id] - v.pt())
                if (dist < radius) and not key in inserted:
                    inserted.add(v.key())
                    PuQ.add_view(v)
        if im_id in q.views:
            for v in q.views[im_id]:
                key = v.key()
                dist = np.linalg.norm(vr.R[im_id] - v.pt())
                if (dist < radius) and not key in inserted:
                    inserted.add(v.key())
                    PuQ.add_view(v)
    if not PuQ.not_empty():
        print ('[informed_merge] empty point from merge')
        #ipdb.set_trace()
    return PuQ


def informed_split(vr, p, q):
    A = [v.key() for I in vr.PQ for v in p.views[I]]
    B = [v.key() for I in vr.PQ for v in q.views[I]]
    commonViews = set(A).intersection(B)
    for k in commonViews:
        im_id = k[0]
        p_center, q_center = vr.PQ[im_id]
        pt = [v for v in p.views[im_id] if v.id_keypoint == k[1]][0].pt()
        p_better_than_q = (
            np.linalg.norm(p_center - pt)
            <
            np.linalg.norm(q_center - pt)
            )
        if p_better_than_q:
            to_be_removed = [
                v
                for v in q.views[im_id]
                if v.id_keypoint == k[1]
                ][0]
            q.views[im_id].remove(to_be_removed)
            if len(q.views[im_id]) == 0:
                del q.views[im_id]
        else:
            to_be_removed = [
                v
                for v in p.views[im_id]
                if v.id_keypoint == k[1]
                ][0]
            p.views[im_id].remove(to_be_removed)
            if len(p.views[im_id]) == 0:
                del p.views[im_id]
    #assert p.not_empty() , 'empty point from split'
    #assert q.not_empty(), 'empty point from split'
    return p, q


def make_merge_with_validation(radius, gEpG):
    """
    provide an implementation of a merge function usign multiview validation
    (float) radius is the threshold of the validation filter
    gEpG={(i,j):Fij}  is a dictionary that maps pair of images (by index) to
        fundamental matrices
    return a merge function
        robust_merge: (trackA,trackB)->result_tracks
    """
    def validatedMergeFunctor(trackA, trackB):
        validation_report = validation(trackA, trackB, gEpG, radius)
        if validation_report.merge:
            merged_track = informed_merge(
                validation_report,
                trackA,
                trackB,
                radius=radius)
            return [merged_track]
        else:
            track1, track2 = informed_split(validation_report, trackA, trackB)
            return [track1, track2]

    def validatedMergeFunctor_checked_for_empty_points(trackA, trackB):
        return [t
            for t in validatedMergeFunctor(trackA, trackB)
            if t.not_empty()]

    return validatedMergeFunctor_checked_for_empty_points


def make_merge_interactive(
        merge_functor,
        outcome_filter,
        oracle_partition, gEpG,
        outcome_functor=None):
    """
    provide an interactive implementation of the given merge operator
    both input and output are merge functions in the form
        merge_functor:(trackA,trackB)->result_tracks
    """
    _outcome_functor = outcome_functor if outcome_functor else lambda x: x
    get_report = make_print_operation(gEpG, oracle_partition)

    def interactiveMergeFunctor(track_x, track_y):
        tracks_Z = merge_functor(track_x, track_y)
        outcome = MergeOutcome(
            track_x,
            track_y,
            tracks_Z,
            gEpG,
            oracle_partition)
        _outcome_functor(outcome)
        if outcome_filter(outcome):
            print(get_report(track_x, track_y, tracks_Z))
            raise outcome
        return tracks_Z
    return interactiveMergeFunctor


def make_merge_outcome_functor(register):
    register['spilled_oracles'] = Counter()
    register['counter'] = 0
    register['correct'] = 0
    register['recover'] = 0
    register['merge'] = 0
    register['split'] = 0

    def outcome_functor(outcome):
        o = outcome
        register['counter'] += 1
        if o.is_split():
            register['split'] += 1
        else:
            register['merge'] += 1
        if o.is_recover():
            register['recover'] += 1
        if o.is_correct():
            register['correct']
        register['spilled_oracles'] += o.get_spilled_oracles()
    return outcome_functor
