# Shortify  [![Build Status](https://travis-ci.org/kotyara1005/Shortify.svg?branch=master)](https://travis-ci.org/kotyara1005/Shortify) [![codecov](https://codecov.io/gh/kotyara1005/Shortify/branch/master/graph/badge.svg)](https://codecov.io/gh/kotyara1005/Shortify)
Shortify is a bit.ly clone.
## Run app
```
docker-compose up
```
## Run tests
```
docker run --name some-redis -d redis -p 6666:6379
pytest .\shortify\tests.py
```
