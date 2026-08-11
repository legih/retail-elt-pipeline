\# Environment Setup



\## Start Postgres

```bash

docker run --name de-postgres -e POSTGRES\_PASSWORD=devpass \\

&#x20; -e POSTGRES\_USER=dev -e POSTGRES\_DB=warehouse \\

&#x20; -p 5432:5432 -d postgres:16

```



\## Daily use

\- `docker start de-postgres` — start existing container

\- `docker stop de-postgres` — stop it

\- `docker ps` — check it's running



\## Connection details

Host: localhost | Port: 5432

Database: warehouse | User: dev | Password: devpass

