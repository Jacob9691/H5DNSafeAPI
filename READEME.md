# Secure API

Dette projekt implementerer et sikkert REST API med FastAPI, containeriseret med Docker og eksponeret via Nginx med HTTPS.

## Opsætning

### Python

API’et er udviklet i Python ved brug af FastAPI, som er et hurtigt framework til udvikling af REST API’er.

- API’et understøtter flere HTTP-metoder (GET, POST, PUT, DELETE)
- Data valideres ved hjælp af Pydantic-modeller
- API-key autentifikation er implementeret via HTTP-header (`api-key`)
- API-nøglen hentes fra en environment variable og er derfor ikke hardcoded
- Automatisk dokumentation genereres via Swagger UI (`/docs`)

API’et afvikles med Uvicorn, som fungerer som ASGI-server (Asynchronous Server Gateway Interface) og understøtter hot reload under udvikling.

---

### Nginx

Nginx anvendes som reverse proxy og håndterer sikker kommunikation til API’et.

- Nginx lytter på port 443
- HTTPS er konfigureret med et selvsigneret SSL-certifikat
- Alt indgående HTTPS-trafik videresendes til FastAPI-containeren via HTTP på port 8000
- Relevante HTTP-headere videresendes korrekt til backend

Nginx sørger dermed for kryptering af trafikken og adskillelse mellem klient og backend.

---

### Docker

Projektet er containeriseret ved hjælp af Docker og Docker Compose.

- API’et kører i en Python-container baseret på `python:3.11-slim`
- Nginx kører i en separat container baseret på `nginx:alpine`
- Docker Compose bruges til at bygge og starte begge services
- API-nøglen leveres via en `.env`-fil og tilgås som environment variable i containeren

Denne opsætning sikrer en reproducerbar og skalerbar løsning, der er egnet til både udvikling og deployment.

---

## Wazuh – Overvågning og sikkerhed

### Hvad er Wazuh?
Wazuh er et open source sikkerheds- og overvågningsværktøj - SIEM (Security Information and Event Management), som bruges til at overvåge systemer, analysere logfiler og opdage sikkerhedshændelser.  
I dette projekt var målet at bruge Wazuh til at overvåge mit Python REST API og det underliggende Linux-miljø.

Wazuh fungerer ved at indsamle logs og systemdata fra en server via en agent, som sender information videre til en Wazuh Manager, hvor data analyseres og vises i et webbaseret dashboard.

---

### Formål med Wazuh i projektet
Formålet med at inddrage Wazuh var at:

- Overvåge systemets tilstand (CPU, RAM, services)
- Analysere logfiler fra API’et
- Registrere fejl, advarsler og uautoriserede API-kald
- Få et samlet overblik over sikkerhed og drift

Dette understøtter DevNet-principperne om, at sikkerhed og drift er en del af applikationsudviklingen.

---

### Planlagt arkitektur
Den planlagte arkitektur var:

Client (curl / browser)  
→ HTTPS (port 443)  
→ Nginx (reverse proxy)  
→ Python API (Docker / systemd)  
→ Logfiler (log/api.log)  
→ Wazuh Agent  
→ Wazuh Manager & Dashboard  

---

### Udfordringer under opsætning
Under arbejdet med Wazuh opstod flere tekniske udfordringer:

1. **Begrænsninger på arbejdspc**
   Projektet blev udviklet på en arbejdspc med stramme sikkerhedspolitikker (Visma-godkendte applikationer).  
   Dette betød, at installation af systemtjenester som Wazuh Agent ikke var tilladt. Der var heller ikke mulighed for at bruge egen private pc, da den ikke har hardware'et til at understøtte miljøet.

2. **Operativsystem-kompatibilitet**
   Wazuh-installationsscriptet kræver specifikke Linux-distributioner (Ubuntu 22.04, RHEL m.fl.).  
   Det anvendte miljø blev ikke genkendt som understøttet, hvilket forhindrede installation uden brug af `--ignore-check`.

3. **Manglende adgang til Azure skolekonto**
   Den planlagte løsning var at deploye projektet på en cloud-baseret Ubuntu Server (Azure).  
   Men adgang til skolekontoen ikke var mulig, da koden ikke virkede, så kunne denne løsning ikke gennemføres inden for projektets tidsramme.

---

### Refleksion og læring
Selvom Wazuh ikke blev fuldt implementeret i et produktionsmiljø, gav arbejdet en god forståelse af:

- Hvordan logs opstår og bruges i sikkerhedsovervågning
- Sammenhængen mellem API, netværk, logfiler og SIEM-værktøjer
- Hvilke krav sikkerhedsværktøjer stiller til drift og infrastruktur
- Hvorfor cloud- eller dedikerede Linux-servere ofte anvendes til overvågning

Projektet demonstrerer dermed forståelse for DevNet-principper, selvom tekniske begrænsninger forhindrede en fuld implementering.

---

### Fremtidig forbedring
I et produktionsmiljø eller ved adgang til en dedikeret Linux-server (fx cloud VM) ville næste skridt være:

- Installere Wazuh all-in-one på Ubuntu Server
- Integrere API-logfiler direkte i Wazuh
- Opsætte alarmer ved uautoriserede API-kald
- Overvåge API-tilgængelighed og services

---

### REST API
| Endpoint           | Metode | Beskrivelse                              | Kræver API-key? | Eksempel                                                                                                                                                                                                                |
| ------------------ | ------ | ---------------------------------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/status`          | GET    | Tjekker API status                       | Nej             | `curl -k https://localhost/status`                                                                                                                                                                                      |
| `/items`           | GET    | Henter alle items                        | Ja              | `curl -k -H "api-key: supersecretkey" https://localhost/items`                                                                                                                                                        |
| `/items/{item_id}` | GET    | Henter et item via ID                    | Ja              | `curl -k -H "api-key: supersecretkey" https://localhost/items/1`                                                                                                                                                      |
| `/items`           | POST   | Opretter et nyt item                     | Ja              | `bash<br>curl -k -X POST https://localhost/items \ <br>  -H "Content-Type: application/json" \ <br>  -H "api-key: supersecretkey" \ <br>  -d '{"id":3,"name":"Item 3","description":"Third item"}'`                   |
| `/items/{item_id}` | PUT    | Opdaterer et eksisterende item           | Ja              | `bash<br>curl -k -X PUT https://localhost/items/1 \ <br>  -H "Content-Type: application/json" \ <br>  -H "api-key: supersecretkey" \ <br>  -d '{"id":1,"name":"Updated Item 1","description":"Updated description"}'` |
| `/items/{item_id}` | DELETE | Sletter et item via ID                   | Ja              | `curl -k -X DELETE -H "api-key: supersecretkey" https://localhost/items/2`                                                                                                                                            |
| `/search`          | GET    | Søger items efter navn (query parameter) | Ja              | `curl -k -H "api-key: supersecretkey" "https://localhost/search?name=Item"`                                                                                                                                           |
