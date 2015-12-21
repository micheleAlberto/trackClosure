#installare
vedi manuale installazione
#detection and matching
Poste le tracce nella cartella images
```
python -m trackClosure.apps.descriptionMatching images
```
viene creata una cartella data che contiene i file prodotti da openmvg
##come cambiare le impostazioni 
Modificare il file  trackClosure/apps/descriptionMatching.py.
I parametri più interessanti da cambiare sono
*   il tipo di feature
*   il preset ovvero quante feature raccogliere
*   il rapporto minimo tra un candidato di match e il successivo
*   video , se usato, indica la larghezza della finestra di match
``` python
omvg.computeFeatures(
    ['SIFT'|'AKAZE_FLOAT'|'AKAZE_MLDB']
    [,preset=(NORMAL|HIGH|ULTRA)])
omvg.computeMatches(ratio=0.7,video=14)
```

#Tracce
```
python -m trackClosure.apps.descriptionMatching images
```
le componenti connesse si trovano in data/cc/:
*   cc.pk : le tracce originali, reperibili con il modulo python "pickle"
*   cc.txt : le tracce , un keypoint per linea 
    timestamp, track_id, im_id, x, y
*   timestamps.txt  corrispondenza tra im_id e timestamp
