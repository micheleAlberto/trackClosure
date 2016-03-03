#installare
vedi manuale installazione
#detection and matching
Poste le tracce nella cartella images crea una cartella data con i file di openMVG
```
python -m trackClosure.apps.descriptionMatching images data
```
le opzioni rilevanti vengono definite attraverso l' interfaccia utente.
per la fase di detection bisogna scegliere 
*   un descrittore 
*   un preset che indica quante feature per immagine individuare

per la fase di matching bisogna scegliere
*   rapporto di esclusione degli outlier
*   eventuale finestra 

Queste fasi sono implementate da openMVG

#Tracce
```
python -m trackClosure.apps.tracking images data
```
le componenti connesse si trovano in data/cc/:
*   cc.pk : le tracce originali, reperibili con il modulo python "pickle"
*   cc.txt : le tracce , un keypoint per linea 
    timestamp, track_id, im_id, x, y
*   timestamps.txt  corrispondenza tra im_id e timestamp
