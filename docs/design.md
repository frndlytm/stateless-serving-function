# Compensation Imputer

## Problem Statement

Build a step in a pipeline.

Take employee input data as a CSV (attached), fill missing values
in the compensation column through some method (simple is fine,
this is not the focus), and return it in a useful response shape. 

Provide instructions for how to run your process. We are interested
in the design of a system and the structure of the task - not the
specific transformations.

## Solution

Complexity can grow very quickly in solving the above problem,
and ultimately we must make initial design decisions that enable
flexiblility when we are faced with this uncertainty.

What follows is a discussion of the simplest possible solution
that meets the requirements of the above problem, as well as some
design trade-offs we may face when scaling out the simple solution.

### Simple Solution

The simplest possible solution to the above problem already exists
in `sklearn.impute.SimpleImputer`. It is a univariate imputation
strategy that populates missing values in a series with a simple
statistic derived from said series. It implements two standard
pipelining methods that interface nicely with the `sklearn`
pipeline API: `fit` and `transform` (or `fit_transform`).

```python
import pandas as pd
from sklearn.impute import SimpleImputer

df = pd.read_csv(...)
df["compensation"] = (
    SimpleImputer()
    .fit_transform(df["compensation"])
)
print(df)
```

Ultimately, this choice plays poorly with model-based methods
because we rely on the `transform` API typically dedicated to
pre-processing / input shaping.

What if we want to consider _compensation_ as a learned target?

In this case, we prefer the `predict` or `forward` APIs of the
model-based tools.

This introduces our first design cross-road:

- Are we serving a re-usable Transform?
- Or, are we serving a re-usable Model?

Depending on the clients and their use cases, we may choose one
over the other.

For example, if I am a Data Scientist doing feature engineering,
I might prefer an importable Transform from a Python package over
a cloud-hosted transformation so that I can debug the transform
in my IDE, chain it together with other transformations, and not
need to worry about sending requests over the internet.

Alternatively, if I am a Data Analyst seeking recomendations for
a target variable, I might prefer a prediction serving function
because I don't care about the methods, I only care about the
results.

In this particular example, we are predicting a numerical value
that lends itself well to a modeled target variable. Since we
don't know much about the persona seeking these predictions,
a Stateless Serving Function for our model can flexibly serve
all of our use cases.

#### Stateless Serving Function

A Stateless Serving Function effectively puts an ML model behind
an HTTP(S) endpoint in the Cloud and accepts prediction requests.
A Client submits records, and the Service returns predictions.
The Service may pre-process the client record representation
into an input feature representation; however, what is important
is that Clients can clearly associate the predictions back to
their inputs in the format they provided.

```python
import functions_framework

MODEL = get_model()


@functions_framework.http
def function(request):
    data = request.get_json()["data"]
    return MODEL.predict(data)
```

Additionally, a stateless function should not be updating state
variables that impact the predictions mode by the model during
the request, and any given request should be independent from
all other requests to the service.

Note in the above code that we do not update any state about the
model in the scope of a request to the function, we only serve
predictions. Additionally, note that we assume the data in the
request contains then input features in the shape required for
the model.

Next, we discuss two naive approaches to statelessness.

#### Hard-coded Model

Below, we adapt the `transform` interface into the `predict`
interface to enable the `SimpleImputer` to behave like a
predictive model. Additionally, we implement the `get_model`
function from the above example by hard-coding an instance of
our imputer model. This indirection creates a clear boundary
behind which we can add complexity without changing the
architecture.

```python
class SimpleImputerPredictor:
    def __init__(self, target: str, *args, **kwargs):
        self.target = target
        self.imputer = SimpleImputer(*args, **kwargs)

    def predict(self, X: pd.DataFrame) -> pd.Series:
        return self.imputer.fit_transform(X[self.target])


def get_model():
    return SimpleImputerPredictor()
```

#### Per Request Fitting

Notice that we re-fit the model during `predict` in the above code
snippet. This means that for each request to the service, we must
run the full model pipeline (including data splitting if necessary).

In order to fit a model in the scope of a request, either the
client must provide all training / validation / testing data in
the request along with the missing data, or the service needs
a way to get relevant data given the data provided in the request.

It is generally a bad practice for a few reasons:

##### Reason 1: Request Size

The amount of data that must be passed (uncorrupted) over the
network to make valuable predictions introduces transmission
problems potentially requiring streaming architectures to
make feasible.

##### Reason 2: Compute Costs

The computation required to train models on larger and larger
datasets costs money. Training a good model often includes
cross-validation or multiple epochs, which may exceed request
timeouts.

### Adding Complexity

#### Model Registry

We can remove the `fit` step from the above code sample if we
are able to load a pre-trained model from a model registry. This
decouples model training from model serving and enables the
client to submit only records that require predictions in their
requests.

```python
import cachetools
import mlflow


mlflow.set_tracking_uri(tracking_uri="http://127.0.0.1:8080")


@cachetools.func.ttl_cache
def get_model():
    return mlflow.sklearn.load_model(...)

```

#### TTL Model Caching

Additionally, we add a TLL cache to the model getter. While
this has no effect on a hard-coded, per request fitted model,
this enables a

### More Complexity

#### Batch Serving

#### Feature Store

#### Embeddings versus Bridge Schema

#### Keyed Predictions

## References

[0]: https://mlflow.org/docs/latest/traditional-ml/creating-custom-pyfunc/notebooks/introduction.html