# Indicate the openMVG binary directory
OPENMVG_SFM_BIN = "/home/michele/dev/openMVG/build/software/SfM"

# Indicate the openMVG camera sensor width directory
CAMERA_SENSOR_WIDTH_DIRECTORY = "/home/michele/dev/openMVG/openMVG/src/software/SfM" + "/cameraSensorWidth"

KEYPOINT_METHODS=["SIFT","AKAZE_FLOAT","AKAZE_MLDB"]
import os
import subprocess
import sys
from getMatches import getMatches
from parseImages import parseImages
from parseFeat import parseFeat
def imageName2featName(name):
    return name.split(".")[0]+".feat"

class OpenMVG:
    def __init__(self,binary_dir=OPENMVG_SFM_BIN,sensor_dir=CAMERA_SENSOR_WIDTH_DIRECTORY):
        self._bin=binary_dir
        self._cal=sensor_dir
        #input image directory
        self._ind=""
        #computed feature and matches directory
        self._ftd=""
        self.checkBinExist()
        self.image_id2name=None
        self.name2image_id=None
    def checkBinExist(self):
        REQUIRED_BINS=[
            "openMVG_main_SfMInit_ImageListing",
            "openMVG_main_ComputeFeatures",
            "openMVG_main_ComputeMatches",
            "openMVG_main_exportMatches"]
        for b in REQUIRED_BINS:
            assert os.path.isfile(
                os.path.join(self._bin,b) )
    def set_image_dir(self,image_dir):
        self._ind=image_dir
    def set_feature_dir(self,feature_dir):
        self._ftd=feature_dir
        if not os.path.exists(self._ftd):
            os.mkdir(self._ftd)
    def intrinsicsAnalysis(self):
        print ("1. Intrinsics analysis")
        camera_file_params = os.path.join(self._cal, "cameraGenerated.txt")
        pIntrisics = subprocess.Popen([
            os.path.join(self._bin, "openMVG_main_SfMInit_ImageListing"),
            "-i", self._ind,
            "-o", self._ftd,
            "-d", camera_file_params])
        pIntrisics.wait()
        self.loadImageMap()   
        return
    def computeFeatures(self,method="SIFT"):
        assert(method in KEYPOINT_METHODS)
        print ("2. Compute features")
        pFeatures = subprocess.Popen( [
            os.path.join(self._bin, "openMVG_main_ComputeFeatures"),
            "-i", self._ftd+"/sfm_data.json",
            "-o", self._ftd,
            "-m", method] )
        pFeatures.wait()
    def computeMatches(self,ratio=0.8):
        print ("3. Compute matches")
        pMatches = subprocess.Popen( [
            os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),
            "-i", self._ftd+"/sfm_data.json",
            "-o", self._ftd,
            "-r", str(ratio)] )
        pMatches.wait()
    def exportKeypoints(self):
        print ("Export keypoints")
        pExportKeypoints=subprocess.Popen( [
            os.path.join(OPENMVG_SFM_BIN, "openMVG_main_exportKeypoints"),
            "-i", self._ftd+"/sfm_data.json",
            "-d", self._ftd,
            "-o", self._ftd ] )
    def getMatches(self):
        return getMatches(
        #feat directory
            self._ftd,
        #sfm file
            (self._ftd+"/sfm_data.json"),
        #match file
            (self._ftd+"/matches.f.txt"))
    def loadImageMap(self):
        sfm_file_name =self._ftd+"/sfm_data.json"
        self.image_id2name,self.name2image_id = parseImages(sfm_file_name)
        return self.image_id2name,self.name2image_id
    def getFeats(self,image_id):
        if not self.image_id2name:
            self.loadImageMap()
        feat_file_name=os.path.join(
            self._ftd,
            imageName2featName(
                self.image_id2name[image_id]))
        return parseFeat(feat_file_name)

def main(argv):
    print "wrapper=OpenMVG()"
    wrapper=OpenMVG()
    raw_input("Press Enter to continue...")
    print "wrapper.set_image_dir(argv[1])"
    wrapper.set_image_dir(argv[1])
    raw_input("Press Enter to continue...")
    print "wrapper.set_feature_dir('./featDir')"
    wrapper.set_feature_dir("./featDir")
    raw_input("Press Enter to continue...")
    print 'wrapper.intrinsicsAnalysis()'
    wrapper.intrinsicsAnalysis()  
    for im in wrapper.image_id2name:
        print im,":",wrapper.image_id2name[im]
    #viene creato sfm_data.json in /matchDir
    raw_input("Press Enter to continue...")
    print 'wrapper.computeFeatures()'
    wrapper.computeFeatures()
    #viene creato image_describer.json in /matchDir
    #viene creato __img__.feat in /matchDir per ogni immagine
    #viene creato __img__.desc in /matchDir per ogni immagine
    raw_input("Press Enter to continue...")
    print 'wrapper.computeMatches()'
    wrapper.computeMatches()
    raw_input("Press Enter to continue...")
    print 'matches=wrapper.getMatches()'
    matches=wrapper.getMatches()
    print "matches: ",matches
    for pair in matches:
        print "PAIR:",pair," matches:",len(matches[pair])
    raw_input("Press Enter to continue...")
    print 'F3=wrapper.getFeats(3)'
    F3=wrapper.getFeats(3)
    print F3
    
if __name__ == "__main__":
    argv=sys.argv
    main(argv)