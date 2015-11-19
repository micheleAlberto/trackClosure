#Open Multi View Geometry Wrapper : class OpenMVG


'''python
from wrapper import OpenMVG
wrapped=OpenMVG(
    binary_dir="/path/to/openMVG/software/SfM"
    sensor_dir="/path/to/openMVG/software/SfM/cameraSensorWidth")
'''
##provide images to be processed
'''python
wrapped.set_image_dir("images/")
'''
jpg files in the provided folder will be analized
##set a folder for the features
'''python
wrapped.set_feature_dir("features/")
'''
if ./features/ does not exist it will be created
##Collect images and their calibration info
'''python
wrapped.intrinsicsAnalysis()
'''
##Compute Features
'''python
wrapped.computeFeatures()
#is equivalent to 
wrapped.computeFeatures(method="SIFT")
'''
is a wrapper for openMVG_main_ComputeFeatures

##Compute Matches
'''python
wrapped.computeMatches(ratio=0.8)
'''
ratio is the rejection coefficient

## reading matches
'''python
matches=wrapped.getMatches()
'''
matches are provided as a dictionary that maps pair of image indexes to the list of their matching keypoints

{(im_a,im_b)-> [ (kp_a,xyso_a,kp_b,xyso_b), ...] }

## reading features
'''python
feats_for_image_4=wrapped.getFeats(4)
'''
Features are provided as numpy arrays



