# Shortify
Shortify is a bit.ly clone.
## Run app
`docker-compose up`
## Run tests
`docker run --name some-redis -d redis -p 6379:6379
pytest .\shortify\tests.py`