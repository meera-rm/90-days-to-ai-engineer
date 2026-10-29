
Write str | None when “no value” is a real, expected answer, not a mistake. If the value should always be there, write plain str and make missing data an error. The rule. Ask yourself: can this legitimately not exist? If yes, use str | None. If no, use str. Don’t add | None “just to be safe.” Every | None forces every user of that value to handle the empty case, and the checker will make them. When you’d use str | None:

Truly optional data. A middle name, a nickname, or a phone number someone didn’t give.

python

python
  @dataclass
  class User:
      first_name: str
      middle_name: str | None = None
Optional parameters with a default. For example, “use this file path if given, otherwise use the default one.”

When you’d keep plain str:

Required data. Email, username, IDs. If it’s missing, raise an error early rather than passing None around.
When an empty string is enough. If "" and “missing” mean the same thing to your program, plain str with "" is simpler.

python
"""
Python Type Challenges — solutions from this session
https://github.com/laike9m/Python-Type-Challenges
"""
from collections.abc import Buffer
from typing import Final, NotRequired, Required, TypedDict, Unpack
# -----------------------------------------------------------------------------
# 1. Buffer
# Annotate read_buffer, which accepts anything that is a buffer.
# -----------------------------------------------------------------------------
def read_buffer(b: Buffer):
    ...
# -----------------------------------------------------------------------------
# 2. Optional argument
# foo can accept an integer argument, None or no argument at all.
# -----------------------------------------------------------------------------
def foo_optional(x: int | None = None):
    ...
# -----------------------------------------------------------------------------
# 3. Final list
# my_list can't be reassigned (contents can still change).
# -----------------------------------------------------------------------------
my_list: Final[list[int]] = []
# -----------------------------------------------------------------------------
# 4. TypedDict
# Student is a dict with keys: name (str), age (int), school (str).
# -----------------------------------------------------------------------------
class Student(TypedDict):
    name: str
    age: int
    school: str
# -----------------------------------------------------------------------------
# 5. TypedDict with an optional key
# Same as above, but school can be left out.
# -----------------------------------------------------------------------------
class StudentOptionalSchool(TypedDict):
    name: str
    age: int
    school: NotRequired[str]
# -----------------------------------------------------------------------------
# 6. TypedDict where only one key is required
# Keys: name, age, gender, address, email. Only name is required.
# -----------------------------------------------------------------------------
class Person(TypedDict, total=False):
    name: Required[str]
    age: int
    gender: str
    address: str
    email: str
# -----------------------------------------------------------------------------
# 7. kwargs with Unpack
# foo expects two keyword arguments: name (str) and age (int).
# -----------------------------------------------------------------------------
class NameAge(TypedDict):
    name: str
    age: int
def foo_kwargs(**kwargs: Unpack[NameAge]):
    ...

coerys type hint problems
type as is

Created a file, shared a file
I saved your solutions exactly as written in type_hint_challenges.py. Below is a short explanation of each one.

In-depth explanations

Buffer (collections.abc.Buffer)
A buffer is any object that exposes raw bytes in memory, such as bytes, bytearray, memoryview, or a NumPy array. Think of it as anything you can read as a row of numbered boxes, each holding a byte. Annotating with Buffer says “give me anything shaped like that,” not just one specific class. It was added in Python 3.12 through PEP 688. Real-world use: a function that hashes or uploads binary data, like streaming a file to S3, should accept bytes and memoryview alike.

Optional argument (int | None = None)
There are two separate ideas here. int | None says the value can be an int or nothing. = None says you’re allowed to leave the argument out. Imagine a pizza order where “extra cheese” can be a number of scoops, “no thanks,” or not mentioned at all. A common mistake is to write x: int = None, which type checkers reject because None isn’t an int. Real-world use: def fetch_users(limit: int | None = None), where None means no limit.

Final (Final[list[int]])
Final locks the name, not the contents. It’s like a label glued permanently onto a box: you can’t move the label to a different box, but you can still put toys in and take them out. So my_list.append(1) is fine, but my_list = [] is an error. Real-world use: module constants like MAX_RETRIES: Final = 3 or a shared registry list.

TypedDict (Student)
A normal dict[str, Any] says nothing about which keys exist. A TypedDict is a form with named blanks, where each blank has a type. The checker catches typos like student[“nmae”] and wrong types like age="ten". At runtime it’s still a plain dict. Real-world use: typing JSON API payloads or rows from a database before you reach for Pydantic.

NotRequired
By default, every key in a TypedDict must be present. NotRequired[str] marks a single key as optional, like a blank on a form you’re allowed to skip. Real-world use: an API response where school only appears for some users.

total=False + Required
This flips the default. total=False makes every key optional, and Required[...] makes specific keys mandatory again. It’s the cleaner choice when most keys are optional; otherwise you’d write NotRequired four times. Real-world use: a PATCH update payload, where only the ID is required and every other field is “change if present.”

Unpack for **kwargs
Before this, **kwargs: int meant every keyword argument was an int, which couldn’t describe mixed types. Unpack[NameAge] says the keyword arguments must match this TypedDict’s keys and types exactly. It’s like a function saying “pass me a filled-in NameAge form, field by field.” Real-world use: wrapper functions that forward settings, such as def connect(**opts: Unpack[DBOptions]). It was added in Python 3.12 through PEP 692.