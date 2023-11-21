# Compensation Predictor

A serverless, stateless serving function template repo with
deployment tasks and a minimal model asset.

## Development

Google's Functions Framework helps to bridge the gap between
Cloud Functions and Cloud Run with a one-size fits all function
serving entrypoint.

The Cloud Functions service manages the containerization for you
when you deploy it alongside its requirements.

The Cloud Run service expects a container image to deploy it, and
as a result you gain more explicit control over resources.

To get the best of both worlds, we dockerized the Cloud Function
using the functions framework to enable a repeatable local
testing environment and easy migration to Cloud Run if we need
more control over deployment.

### Pre-requisites

In order to run the service, we assume you have Docker Desktop with Docker
Compose installed. [Get Docker here][Docker].

To run the demo, we assume you are able to send requests with Python from
your local machine to the Docker container. If you haven't installed Python,
[pyenv][pyenv] is a great tool for managing multiple versions of Python and a great
choice for installing Python.

### Local

After you have the pre-requisites installed, you can build the service locally
with the following command:

```shell
$ docker compose build
[+] Building 178.3s (11/11) FINISHED
...
```

Once your container image is built, you can run the service locally by running
the following command:

```shell
$ docker compose up
[+] Running 1/0
 ✔ Container compensation-imputer-function-1  C...             0.0s
Attaching to compensation-imputer-function-1
...
```

The function is now running at (http://localhost:8080).

### Testing

To run the example, you need to have a local Python virtual environment set up.

Assuming you're on a Unix-based OS, run the following command to do that:

```shell
$ python -m venv .venv && source .venv/bin/activate
(.venv) $ pip install -r requirements-local.txt
```

Then, you can run a complete demo show request and response structure by
executing:

```shell
(.venv) $ invoke demo
```

## Request Schema

```json
{
  "model_uri": "relative/path/to/Model",
  "target": "compensation",
  "data": {
    "schema": {
      "fields": [...],
      "primaryKey": [...],
      "pandas_version": "1.4.0"
    },
    "data": [...]
  }
}
```

## Response Schema

See, [pandas.DataFrame.to_json(*args, orient="table", **kwargs)][Response Schema].

```json
{
  "schema": {
    "fields": [...],
    "primaryKey": [...],
    "pandas_version": "1.4.0"
  },
  "data": [...]
}
```

[Docker]: https://docs.docker.com/get-docker/
[pyenv]: https://github.com/pyenv/pyenv
[Response Schema]: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html
