#Track Closure

##detectMatch.py
An utility that wraps OpenMvg to perform detection and matching
##epipolarGeometry.py  
A class to keep a graph of multiple view epipolar constraints.
Importing F matrices from matches is implemented using opencv bindings for ransac estimation.
##Tracking.py
An utility to perform closure of tracks from 2-view matches provided by OpenMvg 
##TODO: robustTracking.py
##BenchmarkApp.py
A gui application to assign track oracles to keypoints and save them in a benchmark file
###new benchmark
Create a new, empty, benchmark file with label as label
Example:
```
python BenchmarkApp.py --new benchmark.be benchmark_label
```
###Add a connected component to the benchmark
--addcc *benchmark_file* *epipolar_file* *connected_component_file* *image_directory* *openMVG_directory* list_of_cc_ids

add the connected components from *connected_component_file* identified by list_of_cc_ids to *benchmark_file* for each connected component oracles are to be defined with a point and click GUI

Example:
```
python BenchmarkApp.py--addcc benchmark.be vg.epg cc_tracks.pk images/ matches/  8983 10393 29977 30134 34933 17783
```
### TODO: execute Benchmark
--test *benchmark_file* *epipolar_file* *partition_to_test*

### Components: 

*   OracleGui.py
implementa la gui di benchmarkApp.py
*   benchmark.py
implementa le logiche del benchmark , usato in benchmarkApp

### TODO: live benchmark - interactiveClosure.py
--live *benchmark_file* *epipolar_file* ?
interactively debug robust closure of partitions of benchmark file
stato: in lavorazione
implementa funzioni per realizzare una chiusura robusta controllando ad ogni inserimento di punto
#### Components: 
*   interactiveMerge.py 
*   mergeException.py
*   printOperation.py
*   partitionTransfer.py




