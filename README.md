# Jasmin SMS GUI

A [Py4web](https://py4web.com/) GUI application for managing and monitoring all aspects of a a single instance of the popular open source [Jasmin SMS Gateway](https://github.com/jookies/jasmin) as an alternative to the standard jcli command line interface. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See the relevant deployment documentaion for notes on how to deploy the project on a live system. Installation and setup will vary depending on your operating system and preferred installation method and are covered in great detail in the respective documentation

### Prerequisites

* Python 3
* A working installation of the Jasmin SMS Gateway software with standard jcli port exposed (can be a docFoker container) 
* A working Py4Web installation (either dev or live deployment) which can access jcli port on Jasmin either locally or remotely

### Installing

Depending on your requirements and OS installation will vary. 
Full documentation for the installation and usage for Jasmin SMS Gateway can be found at https://docs.jasminsms.com/en/latest/index.html 
Full documentation for the installation and usage for Py4Web can be found at https://py4web.com/_documentation/static/en/index.html

Example:
To set up a development environment on a Windows 10 machine with WSL2 (Ubuntu) and a dockerised Jasmin follow these steps: 


```
$ docker-compose --version
docker-compose version 1.28.5, build c4eb3a1f
```
If docker is not installed you will need to install it before proceeding

Create a directory to store your docker-compose file

```
$ mkdir /opt/scripts/jasmin
$ cd /opt/scripts/jasmin
```

Create a docker compose file in the directory usind your favourite editor

```
$ vi docker-compose.yml
```
Paste the following into the docker-compose.yml

```
version: "3"

services:
  smppsim:
    image: eagafonov/smppsim
    container_name: smppsim
    ports:
      - 3785:2775
  redis:
    image: redis:alpine
    restart: unless-stopped

  rabbit-mq:
    image: rabbitmq:alpine
    restart: unless-stopped

  jasmin:
    image: jookies/jasmin:0.10
    restart: unless-stopped
    container_name: jasmin
    volumes:
      - /var/log/jasmin:/var/log/jasmin
      #- /etc/jasmin:/etc/jasmin
      - /etc/jasmin/store:/etc/jasmin/store

    ports:
      - 2775:2775
      - 8990:8990
      - 1401:1401
    depends_on:
      - redis
      - rabbit-mq
    environment:
      REDIS_CLIENT_HOST: redis
      AMQP_BROKER_HOST: rabbit-mq
      SMPPSIM: smppsim
```

This includes an smpp simulator in order to test connectivity etc.
Save and close.

Start the Jasmin container
```
$ docker-compose up
```
Check that Jasmin and dependancies are up and running
```
$ docker ps
CONTAINER ID   IMAGE                 COMMAND                  CREATED      STATUS      PORTS                                                                    NAMES
f4cc24abd695   jookies/jasmin:0.10   "/docker-entrypoint.…"   3 days ago   Up 3 days   0.0.0.0:1401->1401/tcp, 0.0.0.0:2775->2775/tcp, 0.0.0.0:8990->8990/tcp   jasmin
794d7b78b76a   redis:alpine          "docker-entrypoint.s…"   3 days ago   Up 3 days   6379/tcp                                                                 jasmin_redis_1
4febaf435594   rabbitmq:alpine       "docker-entrypoint.s…"   3 days ago   Up 3 days   4369/tcp, 5671-5672/tcp, 15691-15692/tcp, 25672/tcp                      jasmin_rabbit-mq_1
5c8b43d5cfc1   eagafonov/smppsim     "/bin/sh -c /opt/loc…"   3 days ago   Up 3 days   0.0.0.0:3785->2775/tcp                                                   smppsim
```
Please refer to the Jasmin manual for troubleshooting if needed 

Create a python3 virtual environment in the location of your choice or follow py4web installation procedures for deployment
```
$ cd /opt
$ python3 -m venv py4web
```
Activate the virtual environment
```
$ source py4web/bin/activate
(py4web)$
```
Install Py4Web in the newly created virtual environment
```
(py4web)$ cd py4web
(py4web)$ python3 -m pip install --upgrade py4web --no-cache-dir
```
Hint: If python3 doesnt work try using just pyhon instead.
This will install py4web and all its dependencies on the system’s path only. The assets folder (that contains the py4web’s system apps) will also be created. After the installation you’ll be able to start py4web on any given working folder with
```
py4web setup apps
py4web set_password
py4web run apps
```
## First Run
```
$ py4web run apps
```
E-xplain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc
