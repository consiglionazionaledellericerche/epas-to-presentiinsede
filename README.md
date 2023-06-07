# epas-to-presentiinsede

*This project is supposed to be used for Italian users. Therefore, the whole content of the generated documents, including the README file, is in Italian language.*

Questo programma offre la possibilità di attivare un servizio web in grado di ottenere informazioni sugli utenti presenti in una determinata sede, sfruttando integrazione con la piattaforma [electronic Personnel Attendance System (ePAS)](https://epas.projects.iit.cnr.it). In particolare, l'utilità nasce nei confronti di servizi di portineria e guardianaggio, al fine di permettere loro di visualizzare chi è presente in sede in un determinato momento.

### Caratteristiche ###

* Accesso e consultazione dei dati tramite interfaccia web
* Integrazione con la piattaforma [electronic Personnel Attendance System (ePAS)](https://epas.projects.iit.cnr.it)
* Supporto a più istituti per la stessa sede
* Deployment sotto forma di container [Docker](https://www.docker.com)
* Possibilità di nascondere i dettagli orari di entrata/uscita dei dipendenti
* Supporto a configurazione in formato [YAML](https://yaml.org)

### Installazione ###

* Clonare il repository:
```
git clone https://github.com/auino/epas-to-presentiinsede.git
```
* Accedere all'interno della directory che contiene i sorgenti del repository:
```
cd epas-to-presentiinsede
```
* Fare la build dell'immagine [Docker](https://www.docker.com):
```
docker build -t epas-to-presentiinsede .
```
* Opzionalmente, salvare l'immagine [Docker](https://www.docker.com) su file:
```
docker save epas-to-presentiinsede:latest|gzip > epas-to-presentiinsede.tar.gz
```

### Configurazione ###

La configurazione avviene attraverso la modifica di due file [YAML](https://yaml.org) all'interno della directory `data`.

* `accounts.yaml` specifica username e password per gli account in grado di poter accedere alla piattaforma: sebbene sia in linea teorica utilizzare autenticazione tramite credenziali SIPER, dal momento che l'utilizzo del software avviene tipicamente da personale esterno (es. personale di servizi esterni di portineria o guardianaggio), si è optato per un utilizzo di credenziali ad-hoc.

Un esempio di contenuto del file è riportato a seguire, dove occorre considerare che viene considerato un singolo utente con nome utente `mario.rossi` e password (memorizzata in chiaro) `password_sicura`:
```
- username: mario.rossi
  password: password_sicura
```

All'interno del file, è possibile inserire più utenti sfruttando la struttura del formato [YAML](https://yaml.org).

* `locations.yaml` specifica la lista di sedi da considerare, dove ogni sede è rappresentata dalla sede dal proprio identificativo

Un esempio di contenuto del file, relativo alla sede CNR-IEIIT di Genova, è riportato a seguire.

```
- id: 222220
  description: CNR-IEIIT Genova
  web: https://www.ieiit.cnr.it
  username: epastopresentiinsede_ieiit_genova
  password: password_sicura
```

Per ottenere l'identificativo della sede (`id`), aprire [ePAS](https://epas.projects.iit.cnr.it) con un account di amministratore tecnico per la sede di riferimento, andare all'interno del menu *Configurazione*, dunque selezionare la voce *Sedi e Amministratori* e cliccare sul nome della sede di riferimento; l'identificativo viene indicato con il termine *Sede Id*.

All'interno del file, è possibile inserire più sedi sfruttando la struttura del formato [YAML](https://yaml.org).

E' possibile applicare altre configurazioni minori attraverso variabili di ambiente condivise con il container [Docker](https://www.docker.com), al momento dell'esecuzione.
Per maggiori informazioni, consultare la sezione relativa all'esecuzione del servizio.

### Esecuzione del servizio ###

Per l'esecuzione del servizio, è possibile definire le seguenti variabili di ambiente:
* `secretkey` (obbligatoria): identifica la [chiave segreta](https://flask.palletsprojects.com/en/2.3.x/config/#SECRET_KEY) utilizzata per la generazione e memorizzazione dei cookie di sessione
* `showdetails` (opzionale, default = `0`): se impostata a `1`, mostra i dettagli orari per ogni singola unità di personale
* `refreshtimeout` (opzionale, default = `0`, dunque, disabilitata): imposta dopo quando tempo, in secondi, viene aggiornata in automatico la pagina web che mostra gli utenti presenti in sede; si consiglia di utilizzare un valore non particolarmente basso, in quanto potrebbe portare a blocchi da parte della piattaforma piattaforma [ePAS](https://epas.projects.iit.cnr.it) dovuti ad un numero eccessivo di richieste

Un esempio di utilizzo viene riportato in seguito.
```
docker run -v $PWD/data:/data -e secretkey=12345 -e showdetails=1 -e refreshtimeout=600 -p 8090:5000 epas-to-presentiinsede
```
dove occorre considerare che:
* `$PWD/data` identifica il percorso sull'host della directory che contiene i due file `accounts.yaml` e `locations.yaml`, debitamente compilati
* `8090` identifica la porta in ascolto sull'host (mentre il container si mette in ascolto sempre sulla porta `5000`)

### Utilizzo del sistema ###

E' necessario accedere al portale attraverso l'indirizzo web dello stesso, sulla porta utilizzata (nell'esempio, `8090`).
Tale indirizzo di accesso viene solitamente fornito solo una volta completata l'installazione.

Una volta aperto il sito all'indirizzo corretto, viene richiesto all'utente di effettuare login al portale, sfruttando le credenziali memorizzate all'interno del file `accounts.yaml`.

Una volta autenticati, verrà mostrata la pagina web che riporta i dettagli sulle persone attualmente presenti in sede.
In base alla configurazione scelta in fase di installazione, tale pagina viene aggiornata automaticamente.

### Possibili miglioramenti ###

Consultare la [roadmap del progetto](https://github.com/orgs/consiglionazionaledellericerche/projects/4).

### Contatti ###

[Enrico Cambiaso](https://www.ieiit.cnr.it/people/Cambiaso-Enrico)
