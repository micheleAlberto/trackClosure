#how to install

what you need:
*   opencv2.8+ , w/ Python
*   numpy
*   openMVG

python -m trackClosure.apps.descriptionMatching images
python -m trackClosure.apps.tracking images
python -m trackClosure.apps.BenchmarkApp --new data/prova.be prova1
python -m trackClosure.apps.BenchmarkApp --addcc data/prova.be data/matches.epg data/cc.pk nave data 129825

