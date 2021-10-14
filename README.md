# LemonSSO :lemon:

Servizio di sso per tutorial Python

## Env vars :book:
- `DEBUG` - modalità debug on/off (Boolean) -> Default `false`
- `MONGO_URL` -  URL MongoDB
- `MONGO_DATABASE` -  Nome Database MongoDB
- `ADMIN_APIKEY` -  API-Key utente Admin
- `SERVER_BINDS` - Socket TCP su cui effettuare il bind della porta del server separati da `;` -> Default `localhost:8000`
- `SERVER_LOGLEVEL` - Livello di verbosità dei log -> Default `info`
- `SERVER_WORKERS_NUM` **Solo Produzione** Numero di worker per il server ASGI -> Default `{CPU_CORES} * 2 + 1`