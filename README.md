# Shortify
Shortify is a bit.ly clone. [![Build Status](https://travis-ci.org/kotyara1005/Shortify.svg?branch=master)](https://travis-ci.org/kotyara1005/Shortify)
## Run app
```
docker-compose up
```
## Run tests
```
docker run --name some-redis -d redis -p 6379:6379
pytest .\shortify\tests.py
```
