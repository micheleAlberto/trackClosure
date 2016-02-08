import sys
import numpy as np
from pick import pick
from ..src.fromOpenMVG.wrapper import OpenMVG, KEYPOINT_METHODS


def DESCRIPTION_MATCHING(image_dir,omvg_dir):
    omvg=OpenMVG()
    omvg.set_feature_dir(omvg_dir)
    omvg.set_image_dir(image_dir)
    omvg.intrinsicsAnalysis()
    omvg.computeFeatures(KEYPOINT_METHODS[2],preset='HIGH')
    omvg.computeMatches(ratio=0.7,video=30)


def pick_preset():
    options=["NORMAL","HIGH","ULTRA"]
    option, index = pick(options, "how many features do you want?")
    return option

def pick_describer():
    option, index = pick(KEYPOINT_METHODS, "what kind of feature do you want?")
    return option

def pick_outlier_rejection():
    options=map(str,[0.95,0.9,0.8,0.7,0.6,0.5])
    option, index = pick(options,"outlier rejection ratio")
    return float(option)

def pick_window():
    options=['all matches','3','5','7','10','15','20','32']
    option, index = pick(options,"all matches or just a window?")
    if index==0:
        return 0
    else:
        return int(option)

def ask(s):
    options=['yes','no']
    option, index = pick(options,s)
    return ('yes' in option)

def PIPELINE(image_dir,omvg_dir):
    omvg=OpenMVG()
    omvg.set_feature_dir(omvg_dir)
    omvg.set_image_dir(image_dir)
    perform_intrinsic=ask("perform image initialization ?")
    perform_detection=ask("perform keypoint detection and description ?")
    if perform_detection:
        method=pick_describer()
        preset=pick_preset()
    perform_matching=ask("perform feature matching ?")
    if perform_matching:
        r= pick_outlier_rejection()
        w=pick_window()
    if perform_intrinsic:
        omvg.intrinsicsAnalysis()
    if perform_detection:
        omvg.computeFeatures(method,preset=preset)
    if perform_matching:
        if w==0:
            omvg.computeMatches(ratio=r)
        else:
            omvg.computeMatches(ratio=r,video=w)
    

if __name__ == "__main__":
    assert(len(sys.argv)>2)
    PIPELINE(sys.argv[1],sys.argv[2])




