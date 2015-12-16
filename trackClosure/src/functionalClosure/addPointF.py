"""
This module deals with add point procedures.
Add point procedure have the signature:
add_point_functor(partition, track)

the input partition is modified in place to accomodate the new track

add point procedures are called by closure functions

note about partition.newPoint:
    def newPoint(self,views):
        pointId=0
        p=point(pointId,views)
        self._insertPoint(p)
        return p
"""


def make_add_point(SynthPoints_functor):
    def add_point_functor(partition, track):
        lock_label = -track.id
        matching_tracks = partition.viewGroupQuery(track.views)
        if len(matching_tracks) == 0:
            partition.newPoint(track.allViews())
            return
        #acquire lock point
        locked_points = [partition.points[l] for l in matching_tracks]
        locked_views = []
        for p1 in locked_points:
            locked_views += partition.lockPoint(p1, label=lock_label)
        #synthesys
        new_points = SynthPoints_functor(track, locked_points)
        new_views = set([v.key() for p in new_points for v in p.allViews()])
        #insert new tracks in the partition
        for new_point in new_points:
            partition._insertPoint(new_point, onLock=lock_label)
        #clean missing view points from the view index
        missing_views_to_clear = set(locked_views)
        missing_views_to_clear.difference_update(new_views)
        for im, kp in missing_views_to_clear:
            assert(partition.views[im][kp] == lock_label)
            del partition.views[im][kp]
        return
    return add_point_functor


