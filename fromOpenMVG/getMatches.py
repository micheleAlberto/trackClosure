from parseFeat import parseFeat
from parseMatches import parseMatches
from parseImages import parseImages
import os

"""
GOAL: generate a map of matches from a given pair of images
{(im_a,im_b)-> [ (kp_a,xyso_a,kp_b,xyso_b), ...] }


"""


def featNamer(featDir):
    def foo(filename):
        return os.path.join(featDir,filename.split('.')[0]+'.feat')
    return foo

def getMatches(featDir,sfm_file_name,match_file_name):
    """provide a dictionary of matches
        featDir is the path of the directory that contains the .feat files
        sfm_file_name is the path of sfm_data.json
        match_file_name is the path of the match file (matches.f.txt)
        
        returns:
        a dictionary 
            keys: pair of image identifier (im_id0,im_id1)
            values: list of match tuples
        a match tuple is a 4-uple:
            (kp_id0,feat0,kp_id1,feat1)
        a feat is a numpy float array representing the keypoint tuple:
            x,y,scale,orientation (aka xyso feature)
    """
    print "[getMatches(featDir,sfm_file_name,match_file_name)]"
    print "featDir ", featDir
    print "sfm_file_name " ,sfm_file_name 
    print "match_file_name", match_file_name
    id2name,name2id=parseImages(sfm_file_name)
    pair2matches=parseMatches(match_file_name)
    #check completeness 
    for p in pair2matches:
        assert p[0] in id2name
        assert p[1] in id2name
    featname=featNamer(featDir)
    matchMap={ 
        pair:[
            #let F0 be parseFeat(featname(id2name(pair[0])))
            #let F1 be parseFeat(featname(id2name(pair[1])))
            (match[0],F0[match[0]],
             match[1],F1[match[1]])
            for F0 in (parseFeat(featname(id2name[pair[0]])),) 
            for F1 in (parseFeat(featname(id2name[pair[1]])),)
            for match in pair2matches[pair]]
        for pair in pair2matches}
    return matchMap

