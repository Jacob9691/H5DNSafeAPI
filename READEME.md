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
