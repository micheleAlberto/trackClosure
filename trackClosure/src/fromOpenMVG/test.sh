
python tracking.py -I images/ -M matches/ -SFM matches/sfm_data.json -ot cc_tracks.pk -of vg.epg
#TODO scrivi i metodi in tracking per questo
#--new benchmark_file label
python BenchmarkApp.py --new benchmark.be primo

#--addcc benchmark.be vg.epg cc_tracks.pk images/ matches/  8983 10393 29977 30134 34933 17783
python BenchmarkApp.py --addcc benchmark.be vg.epg cc_tracks.pk images/ matches/  8983 10393 29977 30134 34933 17783

python BenchmarkApp.py --addt benchmark.be vg.epg cc_tracks.pk images/ matches/  robust_tracks.pk 8983 10393 29977 30134 34933 17783
