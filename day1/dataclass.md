use of data class
Use a dataclass when the class’s main job is holding data. The data can be any type, not just numbers: strings, lists, dates, `None`, even other dataclasses.
1. Explanation
Like you’re 10: a dataclass is a labeled storage box. It can hold anything — numbers, words, lists, other boxes — and it can still have a few small helper tricks. What makes it a dataclass is that its main purpose is holding stuff, not doing stuff.
Any value types are fine:
python

```python
from dataclasses import dataclass, field
from datetime import date

@dataclass
class Address:
    city: str
    zip_code: str

@dataclass
class User:
    first_name: str                                  # text
    age: int | None                                  # number or nothing
    signup_date: date                                # date
    tags: list[str] = field(default_factory=list)    # list
    address: Address | None = None                   # another dataclass
```

Methods are allowed too, as long as data is the main point:
python

```python
@dataclass
class User:
    first_name: str
    last_name: str

    def full_name(self) -> str:                      # small helper: fine
        return f"{self.first_name} {self.last_name}"
```

A better test: is it data or a doer?

* Data, so use a dataclass: user, product, order, config settings, a row from a CSV or database table, an API response, a point `(x, y)`, an RGB color.
* Doer, so use a plain class: a database connection, an HTTP client, a file reader, a payment service. These are mostly behavior and hidden internal state (open connections, retries, caches). Printing them or comparing two of them with `==` makes no sense, so dataclass features don’t help.
* Behavior means the things an object does: its actions. Data is what an object has: its facts.
1. Explanation
Like you’re 10: think of a dog. Its data is its name, age and fur color, facts you could write on a card. Its behavior is barking, fetching and eating, things it does. A dataclass is mostly the card. A “behavior” class is mostly the dog doing things.
In code, behavior means methods that take action. Data is stored in fields; behavior lives in methods (functions inside a class) that do work, such as:
   * Talking to the outside world: connecting to a database, calling an API, reading or writing files, sending emails.
   * Changing over time: opening and closing, counting retries, keeping a cache, tracking whether it’s logged in.
   * Running a process: steps like validate, transform, upload, then retry if something failed.
Side by side:
python

```python
from dataclasses import dataclass

# DATA: facts about an order. Mostly fields.
@dataclass
class Order:
    order_id: int
    customer: str
    total: float


# BEHAVIOR: something that DOES things with orders. Mostly methods.
class OrderUploader:
    def __init__(self, bucket: str):
        self.bucket = bucket
        self.connection = None       # hidden internal state
        self.failed_count = 0        # changes as it works

    def connect(self) -> None:       # action: opens a connection
        ...

    def upload(self, order: Order) -> None:   # action: sends data somewhere
        ...

    def retry_failed(self) -> None:  # action: redoes failed work
        ...
```

`Order` just is something. `OrderUploader` does something.
Why this decides dataclass vs plain class. Dataclass features only make sense for data:
   * Printing: printing an `Order` shows useful facts. Printing an `OrderUploader` would show connection objects and counters, which aren’t useful.
   * `==`: two orders with the same facts are the same order. Two uploaders being “equal” doesn’t mean anything.
A small helper method is still fine in a dataclass. `full_name()` or `total_with_tax()` calculates from the object’s own data, without connecting anywhere or changing anything. Those are fine. Once a class mostly acts — connects, sends, saves, retries — it’s a behavior class.
Real-world example: in a data pipeline, the CSV rows become dataclasses (`Customer`, `Order`), which is data. The pieces that read the file, clean the rows, and write to S3 or Postgres are behavior classes or plain functions.
