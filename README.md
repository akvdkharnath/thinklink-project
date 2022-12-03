# THINKLINK PROJECT

This is a REST API app that continuously monitors the price of Bitcoin using a third-party API and alerts a given email when the price either goes above or below given limits.

This application has only one api /api/prices/btc it results list of records based on the given data, offset and limit

## How to start server 
please execute the following command

1. clone this project using 
```bash
    git clone https://github.com/akvdkharnath/thinklink-project.git
```

2. execute following commend to start server 
```bash
    docker-compose up
```

3. calling API using post-man tool\
    URL: http://localhost:8000/api/prices/btc?date=03-12-2022&offset=0&limit=100\
    METHOD: POST\

4. calling API using CURL
```bash
    curl --location --request GET 'http://localhost:8000/api/prices/btc?date=03-12-2022&offset=0&limit=100'
```


# Pre-request to tun this project
1. Docker
2. Docker Compose
3. Curl