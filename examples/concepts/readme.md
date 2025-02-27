docker run -d \
  -e POSTGRES_DB=aiagent \
  -e POSTGRES_USER=aiagent \
  -e POSTGRES_PASSWORD=qwer1234 \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  pgvector/pgvector:pg16