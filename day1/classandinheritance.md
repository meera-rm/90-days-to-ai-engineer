Part 1: The Basic Idea
What is a class?

A class is like a cookie cutter. It’s a shape you design once.
An object is a cookie you make with it. You can make as many cookies as you want, and each one can have different sprinkles.

python
class Car:
   def __init__(self,color,mileage):
      self.color=color
      self.mileage=mileage

  def __str__(self):
      return f"The {self.color} car has {self.mileage:,} miles"


blue_car = Car(color="blue", mileage=20_000)
red_car = Car(color="red", mileage=30_000)
for car in (blue_car, red_car):
  print(car)
red= Car('red',1000)
blue=Car('blue',4000)
print(red)
print(blue)

What each piece does:

class Car: designs the cookie cutter called Car.
__init__ is the “getting ready” step. It runs automatically every time you make a new car. It writes the car’s color and mileage onto that car.
self means “this exact car I’m working on right now.” When you make blue_car, self is blue_car. When you make red_car, self is red_car.
__str__ is the “introduce yourself” step. When you print(car), Python asks the car to describe itself, and this method gives the answer.
{self.mileage:,} puts commas in big numbers, so 20000 becomes 20,000.
20_000 is just 20000. The underscore makes it easier for humans to read, like a comma.

If it ran, it would print:

The blue car has 20,000 miles
The red car has 30,000 miles
The red car has 1,000 miles
The blue car has 4,000 miles

⚠️ Oops in this code: Python is very picky about spaces at the start of lines. Here __init__ starts with 3 spaces and __str__ starts with 2. Python gets confused and stops with an IndentationError. The fix is to use 4 spaces for both, so they line up.

What is inheritance?

Imagine your family has a recipe book. When you’re born, you get to use the whole family recipe book without writing it yourself. That’s inheritance.

But maybe you like your pancakes with chocolate chips. So you write your own pancake recipe on a sticky note and put it on top. Now when someone asks you for pancakes, you use your sticky note, not the family recipe. That’s overriding.

python
class Dog:
    species = "Canis familiaris"

    def __init__(self, name, age, breed):
        self.name = name
        self.age = age
        self.breed = breed

    def __str__(self):
        return f"{self.name} is {self.age} years old"

    def speak(self, sound):
        return f"{self.name} says {sound}"




class JackRussellTerrier(Dog):
    def speak(self, sound="Arf"):
        return f"{self.name} says {sound}"

class Dachshund(Dog):
    pass

class Bulldog(Dog):
    pass

>>> miles = JackRussellTerrier("Miles", 4)
>>> miles.speak()
'Miles says Arf'

>>> miles.speak("Grrr")
'Miles says Grrr'
Dog is the parent. It’s the family recipe book.
species = "Canis familiaris" is a class attribute. It’s a fact written on the cookie cutter itself, so every dog shares it.
class JackRussellTerrier(Dog): means “a Jack Russell Terrier is a kind of Dog.” The (Dog) in brackets is how you say “my parent is Dog.”
Dachshund and Bulldog just say pass, which means “I’m not adding anything.” They use everything from Dog as is. That’s pure inheritance.
JackRussellTerrier writes its own speak. That’s the sticky note. It’s overriding.

Why did Jack Russell override speak?
In Dog, speak(self, sound) needs you to tell it a sound. If you call speak() with nothing, it complains.
In JackRussellTerrier, sound="Arf" is a default. That means “if nobody tells me a sound, I’ll just say Arf.”

So:

miles.speak() → no sound given → uses the default → 'Miles says Arf'
miles.speak("Grrr") → you gave a sound → uses yours → 'Miles says Grrr'

⚠️ Oops in this code: Dog needs three things to make a dog: name, age, and breed. But JackRussellTerrier("Miles", 4) only gives two. Python says “you forgot something!” with a TypeError. You can fix it by giving a breed, as in JackRussellTerrier("Miles", 4, "JRT"), or by removing breed from Dog. (In Real Python’s version, Dog doesn’t have breed, because the kind of class is the breed.)

How does Python decide which recipe to use?

When you call miles.speak(), Python goes looking for speak in a line, one stop at a time:

🐶 Miles himself. Does he have his own speak? No.
📒 JackRussellTerrier. Does this class have speak? Yes! Use it and stop looking.
📕 Dog. Only checked if step 2 didn’t have it.
📗 object. The great-great-grandparent of every class in Python.

The first one found wins. Python never even looks further.

This line has a fancy name: the MRO, or Method Resolution Order. You can see it yourself with JackRussellTerrier.__mro__.

Inherited = Python didn’t find it in the child, so it kept walking and found it in the parent.
Overridden = Python found it in the child first, so the parent’s version never got used.
super(): “Ask my parent for help”

Sometimes you want your own sticky note and still want to use the family recipe. Like: “I’ll pick the topping myself, but Grandma, you make the pancake.”

That’s what super() does. It means “go to the next one in the line and ask them.”

python
#access the parent class from inside a method of a child class by using super():

class JackRussellTerrier(Dog):
    def speak(self, sound="Arf"):
        return super().speak(sound)

>> miles = JackRussellTerrier("Miles", 4)
>>> miles.speak() #overridden
'Miles says Arf'

>>> miles.speak("Grrr") #inherited
'Miles says Grrr'

What happens step by step when you call miles.speak():

Python finds speak in JackRussellTerrier (the child).
The child sees no sound was given, so it picks "Arf".
The child says super().speak("Arf"), which means “Dog, you finish this.”
Dog.speak builds the sentence "Miles says Arf" and hands it back.

A small fix to the comments in the code: the comments say one call is “overridden” and the other is “inherited,” but that’s not quite right. Both calls go to the child’s speak first, and both then ask the parent for help.

Call	What happens
miles.speak()	Child runs, picks "Arf", then asks Dog to build the sentence
miles.speak("Grrr")	Child runs, passes "Grrr", then asks Dog to build the sentence

A better way to say it: the default sound comes from the child, and building the sentence comes from the parent. Teamwork!

Class things vs. your own things
python
#Inheritance
class Parent:
    speaks = ["English"]

class Child(Parent):
    def __init__(self):
        super().__init__()
        self.speaks = Parent.speaks + ["German"]

Think of it like this:

Parent.speaks = ["English"] is a list on the family fridge. Everyone in the family can see it and shares it.
Inside Child.__init__, self.speaks = ... gives the child their own list in their own backpack.
When Python looks for speaks on a child, it checks the backpack first. It finds the child’s own list and never looks at the fridge. This is called shadowing. It’s overriding, but for data instead of methods.

Why use + and not .append()?

Parent.speaks + ["German"] makes a brand new list ["English", "German"] and puts it in the child’s backpack. The fridge list stays ["English"]. ✅
If you did self.speaks.append("German"), the child has no list in its backpack yet, so Python would find the fridge list and scribble on it. Now everyone in the family “speaks German.” ❌ That’s a very common bug.

So Child().speaks gives ['English', 'German'], and Parent.speaks is still ['English'].

super().__init__() here means “let my parent do its getting-ready step too.” Parent doesn’t have its own __init__, so Python walks the line to object, which quietly does nothing. That’s fine, and it’s a good habit.

Part 2: A Real-World Example — Getting Data From Different Places

Imagine you work at a company that collects data from lots of places: files in the cloud, websites, and big data folders. Each place is a bit different, but they all do the same basic job: “go get some rows of data.”

So you make one parent class with the basic job, and each child only changes what it needs to.

python
class Extractor:                                   # Parent (like Dog)
    source_type = "generic"                        # class attribute (like species)
    allowed_formats = ["csv"]                      # shared mutable list (like Parent.speaks)

    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __str__(self):
        return f"{self.name} reading from {self.path}"

    def extract(self, batch_size):                 # like Dog.speak(sound)
        return f"{self.name}: pulled {batch_size} rows from {self.path}"


class S3Extractor(Extractor):                      # like Dachshund: inherits everything
    pass


class ApiExtractor(Extractor):                     # like JackRussellTerrier
    source_type = "api"                            # overrides a class attribute

    def extract(self, batch_size=100):             # OVERRIDE: adds a default
        rows = super().extract(batch_size)         # REUSE: parent builds the string
        return rows + " (paginated)"               # EXTEND: child adds its own bit


class ParquetExtractor(Extractor):                 # like Child
    def __init__(self, name, path):
        super().__init__(name, path)               # reuse parent setup
        self.allowed_formats = Extractor.allowed_formats + ["parquet"]  # new list, shadows class attr

Meet the family:

Extractor is the parent. It knows how to remember a name and a path, and how to extract (get) rows.
S3Extractor is like the Dachshund. It says pass and uses everything from the parent. (S3 is Amazon’s cloud storage, like a giant online folder.)
ApiExtractor is like the Jack Russell. It:
Overrides source_type to say "api" instead of "generic".
Overrides extract to add a default of 100 rows.
Reuses the parent with super() to build the sentence.
Extends it by sticking " (paginated)" on the end. (“Paginated” means the website gives data one page at a time, like a book.)
ParquetExtractor is like Child. It lets the parent do its setup with super().__init__(name, path), then gives itself its own list of formats, without touching the parent’s fridge list. (Parquet is a file type used for big data.)

Trying them out:

python
>>> s3 = S3Extractor("sales", "s3://bucket/sales.csv")
>>> s3.extract(500)
'sales: pulled 500 rows from s3://bucket/sales.csv'        # inherited

>>> api = ApiExtractor("orders", "https://api.shop.com/orders")
>>> api.extract()
'orders: pulled 100 rows from https://api.shop.com/orders (paginated)'
>>> api.extract(20)
'orders: pulled 20 rows from https://api.shop.com/orders (paginated)'

>>> pq = ParquetExtractor("events", "/data/events")
>>> pq.allowed_formats, Extractor.allowed_formats
(['csv', 'parquet'], ['csv'])                               # parent untouched
s3.extract(500): S3Extractor has no extract, so Python walks up to the parent and uses that. Inherited.
api.extract(): no number given, so the child uses its default 100, asks the parent to build the sentence, then adds (paginated).
api.extract(20): same, but with 20 instead of 100.
pq.allowed_formats is the child’s own list. Extractor.allowed_formats is still just ['csv']. The fridge list is safe!
Step by step: what happens on api.extract()

It’s like a treasure hunt where Python checks each stop for the extract treasure:

Step	Where Python looks	What happens
1	The object api itself (its own backpack, __dict__)	Only has name and path. No extract. Keep looking
2	ApiExtractor	Found it! Runs it with batch_size=100 (the default)
3	super().extract(100)	“Go to the next stop in line after ApiExtractor,” which is Extractor
4	Extractor.extract	Builds "orders: pulled 100 rows from ..." and hands it back to the child
5	Back in the child	Sticks " (paginated)" on the end and returns the final answer

You can ask Python to show you the line:

python
>>> ApiExtractor.__mro__
(<class 'ApiExtractor'>, <class 'Extractor'>, <class 'object'>)

That reads as: “check ApiExtractor first, then Extractor, then object.”

The four big ideas, side by side
Idea	In kid words	Dog example	Data example
Inherit	“I don’t have my own, so I’ll use my parent’s”	Dachshund gets everything	S3Extractor gets everything
Override	“I have my own sticky note, so I’ll use that”	JackRussellTerrier.speak	ApiExtractor.extract
super()	“I’ll do my part, then ask my parent to do theirs”	default "Arf", parent builds the sentence	default 100, parent builds the sentence, child adds “(paginated)”
Shadowing	“I have my own copy of this thing in my backpack”	Child.speaks	ParquetExtractor.allowed_formats
The classic “scribbling on the fridge” bug

Remember: Python checks your backpack first, then the family fridge. So this line is dangerous:

python
self.allowed_formats.append("parquet")   # BUG

The object has no allowed_formats in its backpack, so Python finds the fridge list (the class one) and changes it. Now every extractor in the whole program thinks it can read parquet files. Yikes!

Using + makes a brand new list and puts it in the object’s own backpack, so the fridge list stays clean. ✅

Where you’ll see this in real programs
Django (a tool for building websites): you override get_context_data(), call super() to get the normal stuff, then add your own extras.
unittest.TestCase (Python’s testing tool): you override setUp() and call super().setUp() so the shared preparation still happens before each test.
Custom errors: class PipelineError(Exception) overrides __init__ and calls super().__init__(message) so Python’s normal error machinery still works.
Rules to remember
Python looks in this order: object → child → parent → object. The first one found wins.
Overriding replaces the method. super() lets you replace it and still use the parent’s version.
If you write your own __init__, call super().__init__(...). Otherwise the parent’s getting-ready step never happens, and things like name and path never get set.
Never change a class’s shared list or dict through self. Make a new one instead.
Part 3: What Happens Under the Hood

Now let’s open up the machine and watch every gear turn. When you run a Python file, it happens in three phases:

🏗️ Building the cookie cutters (defining classes)
🍪 Making a cookie (creating an object)
📞 Asking the cookie to do something (calling a method)

Here’s our example. This time there are two helpers, called mixins, that each add one small extra job:

python
class Extractor:
    def extract(self):
        return "data"

class LoggingMixin(Extractor):
    def extract(self):
        print("LOG: starting extract")
        return super().extract()

class RetryMixin(Extractor):
    def extract(self):
        print("RETRY: attempt 1")
        return super().extract()

class ApiExtractor(LoggingMixin, RetryMixin):
    pass

api = ApiExtractor()
api.extract()
Extractor does the real work: it returns "data".
LoggingMixin writes a note (“I’m starting!”), then passes the job along.
RetryMixin writes a note (“Attempt 1”), then passes the job along.
ApiExtractor(LoggingMixin, RetryMixin) has two parents. The order in the brackets matters: LoggingMixin comes first.

When you run it, you’ll see:

LOG: starting extract
RETRY: attempt 1

and api.extract() gives back "data".

Phase 1: Building the cookie cutters

This happens when Python reads each class block, before any object exists.

Step	What Python does (in kid words)
1	Reads the inside of the class like normal code. def extract makes a function, a little machine that does a job
2	Puts everything from inside the class into a labelled box, a dictionary called Extractor.__dict__, for example {'extract': <function>}
3	Builds the class by calling type("Extractor", (object,), namespace). type is the cookie-cutter factory: every class in Python is made by it
4	Works out the line (the MRO) right now, using a rule called C3, and saves it in Extractor.__mro__
5	Because LoggingMixin.extract uses super(), Python secretly writes a tiny name tag on it: “I belong to LoggingMixin.” The tag is a hidden variable called __class__

Python does this for each class.

ApiExtractor.__dict__ has no extract, because its inside is just pass.

Its line (MRO) works out to:

ApiExtractor → LoggingMixin → RetryMixin → Extractor → object

What is C3? It’s Python’s fair rule for making the line when a class has more than one parent. It makes sure that:

children always come before their parents, and
parents stay in the order you wrote them in the brackets.

If those rules can’t all be true at once, Python stops with a TypeError right here, before you’ve even made an object. It’s like a teacher saying “this seating chart is impossible.”

Phase 2: Making a cookie (api = ApiExtractor())
Step	What Python does
1	Looks for __new__ (the “make an empty thing” step) by walking the line. It finds it way at the end, on object, which creates a blank object
2	Looks for __init__ (the “getting ready” step) the same way. It also finds it on object, which does nothing
3	Gives the new object an empty backpack (__dict__) and a label saying which class it came from: type(api) is ApiExtractor

Important: the object does not get its own copies of the methods. It’s like a kid who doesn’t photocopy the whole family recipe book. Instead, the kid just remembers which family they belong to, and looks up the recipe in the book each time they need it.

Phase 3: Calling api.extract()

Step 1: Find it.
Python walks the line and checks each class’s box (__dict__):

ApiExtractor.__dict__   → no 'extract'
LoggingMixin.__dict__   → found ✅  stop

(It also peeks in api.__dict__, the object’s own backpack, which is empty here.)

Step 2: Attach self.
Python clips api onto the function, like clipping a name badge on. Now it’s a bound method, which means “this function, working for api.” That’s why you never have to type self yourself; Python fills it in.

Step 3: Run LoggingMixin.extract(api).
Python starts a new stack frame, which is like a fresh sheet of paper for this job. It prints LOG: starting extract.

Step 4: Run super().extract().
Writing super() with nothing inside is a shortcut for super(LoggingMixin, api). Python fills in the two blanks by itself:

LoggingMixin comes from the secret name tag (__class__) from Phase 1.
api comes from self, the first thing passed into the method.

Then super looks at the same line (api’s line), skips ahead to the spot just after LoggingMixin, and finds RetryMixin.extract. It clips api onto it too.

🎯 This is the surprising part! LoggingMixin’s parent is Extractor, but super() went to RetryMixin. That’s because super() doesn’t mean “my parent.” It means “the next one in the line of the object I’m working for.” And api’s line has RetryMixin right after LoggingMixin.

Step 5: Run RetryMixin.extract(api).
Another fresh sheet of paper. It prints RETRY: attempt 1. Then super() becomes super(RetryMixin, api), so the search starts just after RetryMixin and finds Extractor.extract.

Step 6: Run Extractor.extract(api), then pass the answer back up.
It’s like a relay race going back to the start. Each runner passes "data" back to the one who called them:

Extractor.extract     returns "data"  ─┐
RetryMixin.extract    returns "data"  ←┘ ─┐
LoggingMixin.extract  returns "data"  ←───┘ → back to you

At the busiest moment, the stack of papers looks like this:

api.extract()
 └─ LoggingMixin.extract(api)
     └─ RetryMixin.extract(api)
         └─ Extractor.extract(api)   ← deepest

Think of it like stacking plates: the last one put on is the first one taken off.

See it yourself

Add this to the bottom of the file and run it:

python
print(ApiExtractor.__mro__)                  # computed in Phase 1
print("extract" in ApiExtractor.__dict__)    # False: inherited, not copied
print("extract" in LoggingMixin.__dict__)    # True: defined here
print(api.__dict__)                          # {}: the object holds no methods
print(api.extract)                           # <bound method LoggingMixin.extract of ...>
print(LoggingMixin.extract.__code__.co_freevars)   # ('__class__',): the hidden super() helper

What each line proves:

Shows the line Python worked out in Phase 1.
False: ApiExtractor doesn’t own extract. It borrows it.
True: LoggingMixin is where extract was really written.
{}: the object’s backpack is empty. No methods were copied in.
Shows the function with api clipped on: a bound method from LoggingMixin.
Shows the secret __class__ name tag that makes super() work.

Want to see the stack of papers? Put import traceback; traceback.print_stack() inside Extractor.extract. Python will print all four frames, from api.extract() at the top down to Extractor.extract at the deepest point.

Rules to remember
Building time: classes are made, and their line (MRO) is worked out and locked in.
Making an object: the object keeps its own data and remembers its class. It does not copy the methods.
Calling time: Python walks the line, clips on self, and runs the method. Each super() keeps walking the same line from where it left off.
Manager badge with super()
1. One-page cheat sheet
The goal

“Stays consistent even when the badge format changes” means the manager’s badge must not copy the employee’s format. It should reuse it through super() and only add the manager-specific part.

Likely starter code
python
class Employee:
    def __init__(self, name, employee_id):
        self.name = name
        self.employee_id = employee_id

    def badge(self):
        return f"{self.name} #{self.employee_id}"
❌ The wrong way: copying the format
python
class Manager(Employee):
    def badge(self):
        return f"{self.name} #{self.employee_id} (Manager)"   # duplicated format

If someone changes Employee.badge to f"[{self.employee_id}] {self.name}", employee badges change but manager badges don’t. The two now look inconsistent.

✅ The right way: override and reuse
python
class Manager(Employee):
    def badge(self):
        return super().badge() + " (Manager)"
python
>>> Employee("Ana", 101).badge()
'Ana #101'
>>> Manager("Raj", 7).badge()
'Raj #7 (Manager)'

Now change only the parent’s format:

python
def badge(self):                          # inside Employee
    return f"[{self.employee_id}] {self.name}"
python
>>> Manager("Raj", 7).badge()
'[7] Raj (Manager)'                       # follows automatically
Step by step: Manager("Raj", 7).badge()
Step	What happens
1	Python walks Manager.__mro__, which is [Manager, Employee, object]
2	Finds badge in Manager.__dict__ and binds self to the Raj object
3	super().badge() searches the MRO after Manager and finds Employee.badge
4	Employee.badge builds "Raj #7" using the current format
5	Back in Manager, " (Manager)" is appended and the result is returned

Manager doesn’t define __init__, so it inherits Employee.__init__. Lookup finds it the same way.

Rules to remember
Override to add behavior, and call super() to reuse the parent’s.
Never duplicate a parent’s format in the child. One source of truth means one place to change it.
This is the same pattern as JackRussellTerrier.speak and ApiExtractor.extract.
2. Top resources with reasoning
Real Python, “Supercharge Your Classes With Python super()”. It has nearly the same exercise, with a child class that extends a parent method instead of rewriting it.
The “DRY principle” (Don’t Repeat Yourself), from The Pragmatic Programmer. This is the design reason behind the exercise: duplicated logic drifts apart over time.
Comparing dataclasses with plain classes' generated methods.
Class vs. dataclass
1. Explanation
The key idea

A dataclass is a regular class. @dataclass is a decorator that takes your class and writes some methods into it based on the fields you list. There’s no new kind of object, no different inheritance, nothing special at runtime.

Think of a regular class as building furniture from raw wood, where you cut every piece yourself. A dataclass is a flat-pack kit: you list the parts, and the standard pieces come pre-cut. It’s the same furniture in the end.

Side by side
python
class PointClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

from dataclasses import dataclass

@dataclass
class PointData:
    x: int
    y: int
python
>>> PointClass(1, 2)
<__main__.PointClass object at 0x10a3f...>     # default repr: useless for debugging
>>> PointData(1, 2)
PointData(x=1, y=2)                            # readable repr

>>> PointClass(1, 2) == PointClass(1, 2)
False                                          # compares identity: different objects
>>> PointData(1, 2) == PointData(1, 2)
True                                           # compares field values
What actually differs
Behavior	Regular class	Dataclass
__init__	You write it	Generated from fields
__repr__	<PointClass object at 0x...>	PointData(x=1, y=2)
==	Same object? (identity)	Same field values?
Hashable (dict key, set)	Yes, by identity	No by default, because __eq__ is defined. Yes with frozen=True
Mutable default like []	Allowed (and a shared-list bug)	Blocked with ValueError, forces default_factory
Immutability	Write it yourself	frozen=True
Ordering (<, sorted)	Write __lt__ etc.	order=True
Fields declared	Anywhere, often in __init__	Top of class, with type hints
Inheritance, super(), methods	Normal	Exactly the same

The hashing row is the one that surprises people. Putting a plain dataclass in a set gives TypeError: unhashable type. That’s deliberate: if equality is based on mutable values, a hash based on them could change while the object sits in the set.

Step by step: PointData(1, 2) == PointData(1, 2)
Step	What happens
1	Python looks up __eq__ on PointData via the MRO
2	Finds the generated __eq__ in PointData.__dict__
3	It checks both objects are the same class
4	Compares (self.x, self.y) == (other.x, other.y) as tuples
5	Returns True

For PointClass, step 2 finds nothing on the class, keeps walking to object.__eq__, which only checks is.

When to use which

Dataclass when the class is mainly data: configs, records, events, API responses after validation, DTOs.

python
@dataclass(frozen=True)
class JobConfig:
    source: str
    target_table: str
    batch_size: int = 1000

Regular class when the class is mainly behavior or manages state and resources: a database connection pool, a service with dependencies, an extractor that opens files, or anything where __init__ does real work instead of just storing arguments.

python
class PostgresExtractor:
    def __init__(self, dsn):
        self._conn = psycopg.connect(dsn)     # does work, not just storing
        self._cursor = None

    def extract(self, query): ...
    def close(self): self._conn.close()

Value equality makes no sense for that extractor. Two connections to the same DSN aren’t “the same thing.”

Quick test: “Would two objects with the same fields be considered equal?” Yes → dataclass. No → regular class.

Rules to remember
A dataclass is a regular class with generated methods. Everything else works identically.
The real behavior changes are == (value vs. identity) and hashing (off by default unless frozen=True).
Data-holding → dataclass. Behavior or resource-holding → regular class.
2. Top resources with reasoning
Python docs, dataclasses, the “Parameters” and __hash__ sections. The exact rules for when __hash__ is generated or set to None, which is the trickiest difference.
Real Python, “Data Classes in Python (Guide)”, the “Alternatives to Data Classes” section. Compares hand-written classes, namedtuples, and dataclasses with the same example.
PEP 557, “Rationale”. Explains what problem the boilerplate-generation solves and why dataclasses are deliberately just normal classes.

real world examples

Real-world dataclass examples
1. Explanation

Each example shows the job the dataclass does, the code, and why a dataclass fits better than a regular class.

1. Pipeline config loaded from YAML

Every pipeline has settings: source, target, batch size, schedule. They’re read once and should never change mid-run.

yaml
# config/orders.yaml
name: orders_daily
source: s3://raw/orders/
target_table: analytics.orders
batch_size: 5000
python
from dataclasses import dataclass
import yaml

@dataclass(frozen=True)
class PipelineConfig:
    name: str
    source: str
    target_table: str
    batch_size: int = 1000

with open("config/orders.yaml") as f:
    config = PipelineConfig(**yaml.safe_load(f))

config.batch_size = 10      # FrozenInstanceError: no accidental changes mid-run

Why a dataclass: it’s pure data, frozen=True protects it, and a typo in the YAML (batchsize) fails immediately with TypeError: unexpected keyword argument instead of silently using the default.

2. Events going to Kafka or S3

A pipeline turns raw rows into typed events, then serializes them.

python
from dataclasses import dataclass, asdict
from datetime import datetime
import json

@dataclass(frozen=True, slots=True)
class OrderPlaced:
    order_id: str
    customer_id: str
    amount_cents: int
    placed_at: datetime

def to_json(event):
    d = asdict(event)
    d["placed_at"] = event.placed_at.isoformat()
    return json.dumps(d)

event = OrderPlaced("o-1", "c-9", 4999, datetime(2026, 10, 27, 9, 30))
producer.send("orders", to_json(event))

Why a dataclass: slots=True cuts memory when you have millions of events, frozen stops later steps from mutating them, and asdict gives the payload in one line.

3. Data quality check results

A validation step runs many checks and needs to report and sort the failures.

python
from dataclasses import dataclass, field

@dataclass(order=True)
class CheckResult:
    severity: int                          # compared first: 1 = critical
    check_name: str
    table: str
    failed_rows: int = field(compare=False)

results = [
    CheckResult(3, "no_future_dates", "orders", 2),
    CheckResult(1, "not_null_order_id", "orders", 41),
    CheckResult(2, "unique_customer_id", "customers", 7),
]

for r in sorted(results):                  # critical first
    print(r)
CheckResult(severity=1, check_name='not_null_order_id', table='orders', failed_rows=41)
CheckResult(severity=2, check_name='unique_customer_id', table='customers', failed_rows=7)
CheckResult(severity=3, check_name='no_future_dates', table='orders', failed_rows=2)

Why a dataclass: order=True makes sorting free (fields compare in declared order), and the readable repr goes straight into logs and Slack alerts.

4. Returning several values from a function

Instead of returning a tuple that callers must unpack in the right order:

python
# Fragile: what's position 2 again?
def load_batch(path):
    ...
    return rows, skipped, duration_s

# Clear
@dataclass
class LoadResult:
    rows_loaded: int
    rows_skipped: int
    duration_s: float

def load_batch(path) -> LoadResult:
    ...
    return LoadResult(rows_loaded=9800, rows_skipped=200, duration_s=4.2)

result = load_batch("s3://raw/orders/2026-10-27.csv")
if result.rows_skipped > 100:
    alert(f"High skip count: {result}")

Why a dataclass: named fields read better, adding a field later doesn’t break callers, and print(result) is useful.

5. Domain models inside an app (Pydantic at the edge)

In a web API, Pydantic validates the incoming request, then the core logic works with plain dataclasses.

python
from pydantic import BaseModel
from dataclasses import dataclass

class CreatePatientRequest(BaseModel):     # boundary: untrusted JSON
    name: str
    birth_year: int

@dataclass
class Patient:                             # internal: already trusted
    patient_id: str
    name: str
    birth_year: int

def create_patient(req: CreatePatientRequest) -> Patient:
    return Patient(patient_id=new_id(), name=req.name, birth_year=req.birth_year)

Why a dataclass: the core logic doesn’t depend on a web framework, and tests can build Patient(...) directly without going through validation.

6. Test fixtures

Tests need lots of slightly different objects.

python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Customer:
    customer_id: str = "c-1"
    country: str = "US"
    is_active: bool = True

base = Customer()
inactive = replace(base, is_active=False)        # copy with one change
uk = replace(base, country="UK")

assert base == Customer()                         # value equality makes asserts easy

Why a dataclass: defaults give a ready “typical” object, replace() makes variations without mutation, and == lets tests compare whole objects.

7. Libraries you’ve probably used
Hugging Face TrainingArguments is a dataclass. That’s why you pass TrainingArguments(output_dir=..., num_train_epochs=3) and its repr prints every setting.
FastAPI accepts dataclasses as request and response models alongside Pydantic.
Where a regular class still wins
python
class S3Client:
    def __init__(self, bucket):
        self._client = boto3.client("s3")     # creates a resource
        self.bucket = bucket

    def list_keys(self, prefix): ...
    def upload(self, path, key): ...

It holds a live connection and is mostly behavior. Two clients for the same bucket aren’t “equal” in any useful sense, so value equality and a generated __init__ add nothing.

Pattern to remember
Job	Dataclass options
Config	frozen=True
High-volume records/events	frozen=True, slots=True + asdict
Sortable results	order=True, field(compare=False) for ignored fields
Multi-value returns	plain @dataclass
Test data	defaults + replace()
Clients, connections, services	regular class