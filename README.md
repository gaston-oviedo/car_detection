# Detections

In a nutshell, this project is an API service that is backed by a Resnet50 model that accepts an image and return the object class and the confidence score. 
The Resnet50 model is trained with imagenet dataset (weights downloaded automatically).

## Project Architecture

The architecture of the project consists of three different services, each of them in a different docker container: **ML Service** where Resnet50 model is based, **API** where the API service is based and finally **REDIS** to conect the previous services. 

![Project Architecture](/tests/Project_arch.png)

## Run the project

After downloading this repository, simply run:

> docker compose up --build -d

The three images will be created and their containers will be up.

There are two ways to run the application, as follow:

### Front-End endpoint

This endpoint (root) takes an image and return the object class and the confidence score.

![Front-End](/tests/Front-End-1.png)

![Front-End](/tests/Front-End-2.png)

### Integration-type endpoint

This endpoint (/predict) takes an image and return the object class and the confidence score in a JSON format without the a UI.


## Tests

### Integration end-to-end

You must have the full pipeline running and [requests](https://docs.python-requests.org/en/latest/) library installed. Then, from this project root folder run:

```
$ python tests/test_integration.py
```

### Modules

We make use of [multi-stage docker builds](https://docs.docker.com/develop/develop-images/multistage-build/) so we can have into the same Dockerfile environments for testing and also for deploying our service.

#### Api

Run:

```bash
$ cd api/
$ docker build -t flask_api_test --progress=plain --target test .
```

You will only need to pay attention to the logs corresponding to the testing code which will look like this:

```bash
#10 [test 1/1] RUN ["pytest", "-v", "/src/tests"]
#10 sha256:707efc0d59d04744766193fe6873d212afc0f8e4b28d035a2d2e94b40826604f
#10 0.537 ============================= test session starts ==============================
#10 0.537 platform linux -- Python 3.8.13, pytest-7.1.1, pluggy-1.0.0 -- /usr/local/bin/python
#10 0.537 cachedir: .pytest_cache
#10 0.537 rootdir: /src
#10 0.537 collecting ... collected 4 items
#10 0.748
#10 0.748 tests/test_api.py::TestIntegration::test_bad_parameters PASSED           [ 25%]
#10 0.757 tests/test_api.py::TestEnpointsAvailability::test_feedback PASSED        [ 50%]
#10 0.769 tests/test_api.py::TestEnpointsAvailability::test_index PASSED           [ 75%]
#10 0.772 tests/test_api.py::TestEnpointsAvailability::test_predict PASSED         [100%]
#10 0.776
#10 0.776 ============================== 4 passed in 0.24s ===============================
#10 DONE 0.8s
```

You are good if all tests are passing.

#### Model

Same as api, run:

```bash
$ cd model/
$ docker build -t model_test --progress=plain --target test .
```
