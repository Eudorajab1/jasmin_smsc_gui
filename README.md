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

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

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
