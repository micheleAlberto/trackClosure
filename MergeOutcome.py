from collections import Counter
from partitionTransfer import dominant
class MergeOutcome(Exception):
    def __init__(self, track_x,track_y,tracks_Z,gEpG,oracle):
        self.track_x=track_x
        self.track_y=track_y
        self.tracks_Z=tracks_Z
        self.xO=Counter(soft_fetch(oracle,track_x))
        self.yO=Counter(soft_fetch(oracle,track_y))
            """
            Errors in the xO/yO track operand
            if len(_O)==0 we don' t kow much about the track because supervised 
                information is not available
            if len(_O)==1 track_y is a correct track as far as we know !!!
            if len(_O)>1  track_y is already wrong before the computation !!!
            """
        self.ZO=[Counter(fetch(oracle,track_z_it)) for track_z_it in tracks_z]
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
        kps2views=lambda some_keypoint_key_sequence :{
            view_key:v 
            for v in track_x.allViews()+track_y.allViews() 
            if view_key==v.key() 
            for view_key in some_keypoint_key_sequence}
        operand_kp=set([v.key() for v in track_x.allViews()+track_y.allViews()])
        result_kp=reduce(
                lambda a,b:a+b,
                [[v.key() for v in track_z ] for track_z in tracks_Z]
                [])
        result_kp=set(result_kp)
        missing = operand_kp.difference(result_kp)
        missing_views=kps2views(missing)
        missing_oracles=soft_fetch_views(oracle,missing_views.values())
        dominant_oracles_of_results=set([dominant(zO) for zO in ZO])          
        self.spilled_oracles=Counter([o 
                for o in missing_oracles
                if o in dominant_oracles_of_results])
        self.spilled=sum(self.spilled_oracles.values())
        pass
    def is_merge(self):
        return len(self.ZO)==1
    def is_split(self):
        return len(self.ZO)==2
    def has_correct_operands(self):
        return (len(self.xO)<2 and len(self.yO)<2)
    def has_known_correct_operands(self):
        return (len(self.xO)==1 and len(self.yO)==1)
    def has_mutually_correct_operands(self):
        return (len(self.xO + self.yO)<2)
    def has_correct_results(self):
        return all( len(zO)<2 for zO in self.ZO)
    def has_known_correct_results(self):
        return all( len(zO)==1 for zO in self.ZO)
    def is_correct(self):
        correct_operation=self.has_correct_results() if self.has_correct_operands() else True
        return correct_operation
    def is_known_correct(self):
        known_correct_operation=self.has_known_correct_results() if self.has_known_correct_operands() else True
        return known_correct_operation
    def is_recover(self):
        self.has_correct_results() and not self.has_correct_operands()
    def is_known_recover(self):
        self.has_correct_results() and not self.has_correct_operands()
    def is_complete(self):
        return (len(self.spilled_oracles)==0)
    def get_spilled(self):
        return self.spilled
    def get_spilled_oracles(self):
        return self.spilled_oracles
    def dominant_x(self):
        return max(self.xO,key=self.xO.get)
    def dominant_y(self):
        return max(self.yO,key=self.yO.get)
    def dominant_results(self):
        return [max(zO,key=zO.get) for zO in self.ZO]
    def is_roughly_correct(self):
        dx=self.dominant_x()
        dy=self.dominant_y()
        if dx and dy:
            zr=self.dominant_results()
            if (dx==dy):
                return dx in zr
            else:
                return (dx in zr) or (dy in zr)
        else:
            return True
    def __str__(self):
        s=  print_merge_operation(track_x,track_y,result,gEpG,oracle)+'\n'
        s+= '\tCorrectness:\n'
        s+= 'correct operands: {}\n'.format(self.has_correct_operands())
        s+= 'correct_results: {}\n'.format( self.has_correct_results() )
        s+= 'recover : {}\n'.format(        self.is_recover())
        s+= 'correct operation: {}\n'.format(self.is_correct())
        s+= 'mutually_correct_operands: {}\n'.format(self.has_mutually_correct_operands())
        s+= 'roughly correct operation: {}\n'.format(self.is_roughly_correct())
        s+= '\tCompleteness:\n'
        s+= 'missing keypoints: {}\n'.format(len(self.missing))
        s+= 'spilled keypoints: {}\n'.format(self.spilled)
        for spilled_oracle in self.spilled_oracles:
            s+= 'spilled {} from oracle {}\n'.format(self.spilled_oracles[spilled_oracle],spilled_oracle)
        return s
