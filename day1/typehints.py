# =============================================================================
#  TYPE HINTS — STUDY NOTES
#  Based on: Corey Schafer, "Python Tutorial: Type Hints - From Basic
#  Annotations to Advanced Generics"
#
#  How to read this file:
#    * Every section starts with "LIKE YOU'RE 10" — a simple picture of the idea.
#    * Then "ENGINEER NOTES" — the real details you need for work/interviews.
#    * Older versions of the code are commented out so you can see how the
#      code evolved. The FINAL version at the bottom is the one that runs.
#
#  Requirements:
#    * Python 3.12+   (for `type X = ...` and `def f[T](...)`)
#    * pip install requests
#    * Optional: pip install mypy types-requests  ->  run `mypy type_hints_notes.py`
# =============================================================================


# =============================================================================
#  SECTION 0 — WHAT IS A TYPE HINT, AND WHY DOES PYTHON HAVE THEM?
# =============================================================================
#
#  LIKE YOU'RE 10:
#    Type hints are labels on lunchboxes. `age: int` is a sticker saying “only
#    whole numbers go here.” Python never reads the stickers, so it lets you
#    put juice in the sandwich box. Your editor and checkers like mypy do read
#    them, and they warn you before you run anything. In real projects, FastAPI
#    reads the same labels to reject bad requests automatically.
#
#  ENGINEER NOTES:
#    * Python is DYNAMICALLY typed: a variable can hold any type, and type
#      mistakes only blow up when that exact line runs (maybe in production).
#    * Type hints are ignored at runtime (no speed cost, no enforcement).
#    * Tools that USE them:
#        - mypy / Pyright / Pylance -> static type checking in editor and CI
#        - Ruff                     -> linting (e.g. "use X | None", "unused import")
#        - FastAPI / Pydantic       -> actually VALIDATE data at runtime from hints
#    * Same idea as TypeScript: types are erased when the code runs. The big
#      difference: TypeScript's build usually fails on type errors; in Python,
#      nothing forces you to run the checker unless you add it to CI.


import random
from dataclasses import dataclass
from typing import Any, NewType, TypeVar

# from typing import Optional        # used in v1 only — later unused (Ruff F401: unused import)
# from typing import TypedDict       # used in v5 only — replaced by @dataclass in v6

import requests  # third-party library for HTTP calls: pip install requests


# =============================================================================
#  v1 — Optional[int]  (the older style shown in the video)
# =============================================================================
#
#  LIKE YOU'RE 10:
#    `Optional[int]` and `int | None` describe a box that holds “a number, or
#    nothing.” Some people tell you their age and some don’t. `|` means “or.”
#    The tricky part is that the label only says empty is allowed.
#    It’s the `= None` default that lets you skip the argument when you call
#    the function.
#
#  ENGINEER NOTES:
#    * Optional[int] means EXACTLY the same as int | None.
#    * Needs `from typing import Optional`.
#    * GOTCHA: "Optional" does NOT make the argument optional to pass!
#      The `= None` default is what lets callers skip it.
#      `Optional` only says None is an ALLOWED VALUE.
#    * `-> dict` is the RETURN type: "this function hands back a dictionary."
#
# from typing import Optional
#
# def create_user(first_name: str, last_name: str, age: Optional[int] = None) -> dict:
#     email = f"{first_name.lower()}_{last_name.lower()}@example.com"
#
#     return {
#         "first_name": first_name,
#         "last_name": last_name,
#         "email": email,
#         "age": age,
#     }
#
# user1 = create_user("Corey", "Schafer", age=38)
# user2 = create_user("John", "Doe")          # age left out -> becomes None


# =============================================================================
#  v2 — int | None  (modern UNION syntax, Python 3.10+)
# =============================================================================
#
#  LIKE YOU'RE 10:
#    The `|` symbol means "OR". `int | None` reads out loud as
#    "a number OR nothing." Same box as before, just a shorter label,
#    and you don't have to import anything to write it.
#
#  ENGINEER NOTES:
#    * This is a UNION type: the value may be any one of the listed types.
#      `str | int` = string or int. `int | None` = nullable int.
#    * Ruff rule UP007 suggests replacing Optional[X] with X | None.
#      After you switch, `Optional` becomes an unused import (Ruff F401) —
#      that's the two warnings you saw in the video's PROBLEMS panel.
#    * TypeScript equivalent: `age: number | null`.
#
# def create_user(first_name: str, last_name: str, age: int | None = None) -> dict:
#     email = f"{first_name.lower()}_{last_name.lower()}@example.com"
#
#     return {
#         "first_name": first_name,
#         "last_name": last_name,
#         "email": email,
#         "age": age,
#     }


# =============================================================================
#  v3 — Typing the dictionary: dict[str, str | int | None]
# =============================================================================
#
#  LIKE YOU'RE 10:
#    Typed dictionaries (`dict[str, ...]`) are a wall of cubbies. Every name
#    tag (key) is words, and every cubby holds certain kinds of stuff. The
#    weakness is that the wall can’t say which cubby holds which kind of stuff.
#
#  ENGINEER NOTES:
#    * dict[KeyType, ValueType]. Here keys are str; values are str | int | None.
#    * Weakness: it can't say WHICH key holds WHICH type. The checker doesn't
#      know "email" is always a str and "age" is int | None. (TypedDict fixes this, v5.)
#    * BUG you hit: `-> dict [str, str | int | None):` — closing with `)` instead
#      of `]` is a SyntaxError. Brackets must match: dict[ ... ]
#
#  PASSING ARGUMENTS (your question: "is user2 created the right way?"):
#    * create_user("Jane", "Doe", 40)      -> POSITIONAL: 3rd value lands in `age`. Valid.
#    * create_user("John", "Doe", age=38)  -> KEYWORD: clearer, preferred for optional args.
#    * create_user("Sam", "Lee")           -> age uses its default None.
#    * create_user(age=40, "Jane", "Doe")  -> SyntaxError: positional must come first.
#    * Tip: `def f(a, b, *, age=None)` — the `*` FORCES callers to write `age=`.
#
# def create_user(first_name: str, last_name: str, age: int | None = None) -> dict[str, str | int | None]:
#     email = f"{first_name.lower()}_{last_name.lower()}@example.com"
#     return {
#         "first_name": first_name,
#         "last_name": last_name,
#         "age": age,
#         "email": email,
#     }
#
# user1 = create_user("John", "Doe", age=38)   # keyword argument
# user2 = create_user("Jane", "Doe", 40)       # positional argument, also correct
# user3 = create_user("Sam", "Lee")            # age defaults to None
#
# Redundant version you wrote and commented out:
#   `Optional[int] | None` = "number or empty, or empty" — says None twice. Use ONE.
# def create_user(first_name: str, last_name: str, age: Optional[int] | None = None) -> dict[str, str | int | None]:


# =============================================================================
#  v4 — TYPE ALIAS: give a long type a short nickname
# =============================================================================
#
#  LIKE YOU'RE 10:
#    Type alias (`type User = ...`) is a nickname. “Alexander Maximilian”
#    becomes “Max,” so you write the long type once and use the short name
#    everywhere.
#
#  ENGINEER NOTES:
#    * `type User = ...`                 -> Python 3.12+ (PEP 695), preferred
#    * `User: TypeAlias = ...`           -> Python 3.10+, needs `from typing import TypeAlias`
#    * `User = ...`                      -> works on 3.9+, but less explicit
#    * An alias is NOT a new type: the checker treats `User` and the long
#      dict type as 100% identical. (Compare NewType in v5.)
#    * TypeScript equivalent: `type User = Record<string, string | number | null>`
#
# type User = dict[str, str | int | None]
#
# def create_user(first_name: str, last_name: str, age: int | None = None) -> User:
#     email = f"{first_name.lower()}_{last_name.lower()}@example.com"
#     return {
#         "first_name": first_name,
#         "last_name": last_name,
#         "age": age,
#         "email": email,
#     }
#
# Older alias styles:
# from typing import TypeAlias
# User: TypeAlias = dict[str, str | int | None]   # Python 3.10+
# User = dict[str, str | int | None]              # Python 3.9+


# =============================================================================
#  v5 — NewType (RGB / HSL) and TypedDict
# =============================================================================
#
#  --- NewType ---
#  LIKE YOU'RE 10:
#    `NewType` (RGB and HSL) works like twins in different-colored wristbands.
#    Both are three numbers, but the checker won’t let an HSL twin through the
#    RGB door. In real code, `UserId` and `OrderId` are both ints, and a
#    `NewType` stops you mixing them up.
#
#  ENGINEER NOTES:
#    * RGB = NewType("RGB", tuple[int, int, int]) creates a DISTINCT type.
#    * Alias vs NewType:
#        type RGB = tuple[...]   -> RGB, HSL and tuple are all interchangeable
#        NewType("RGB", tuple)   -> checker treats RGB, HSL, tuple as different
#    * You must WRAP values: RGB((109, 123, 134)). A plain tuple runs fine,
#      but the checker rejects it.
#    * Zero runtime cost: RGB(x) just returns x. It prints as a normal tuple.
#    * Real world: UserId = NewType("UserId", int); OrderId = NewType("OrderId", int)
#      -> stops you passing an order id where a user id belongs.
#    * TypeScript has no built-in NewType; people fake it with "branded types".
#
#  --- TypedDict ---
#  LIKE YOU'RE 10:
#    `TypedDict` is a school form with labeled blanks: Name (words), Age
#    (number or blank). Now the checker knows exactly what goes in each blank.
#    It’s like a TypeScript `interface`.
#
#  ENGINEER NOTES:
#    * Each key gets its own type -> user["age"] is int | None, user["email"] is str.
#    * At runtime it's still a plain dict: access with user["email"], not user.email.
#    * No default values allowed in TypedDict fields.
#    * TypeScript equivalent: `interface User { email: string; age: number | null }`
#    * Great for JSON / API responses that are already dicts.
#
#  BUGS YOU HIT IN THIS VERSION (kept as lessons):
#    * Fields inside a class must be INDENTED, or Python says IndentationError.
#    * `//` is a JavaScript comment. Python comments use `#`.
#    * Defining `User` twice (TypedDict AND alias) — the second overwrites the first.
#    * RGB was used before it was defined -> define NewTypes ABOVE the class.
#    * `RGB=. NewType(...)` — stray dot is a SyntaxError.
#    * Duplicate dict key "age" — the second silently wins, so age became a string.
#    * `str_age = str(age)` outside the function — `age` only exists INSIDE it.
#
# from typing import NewType, TypedDict
#
# Aliases you commented out — RGB and HSL would be interchangeable:
# type RGB = tuple[int, int, int]
# type HSL = tuple[int, int, int]
#
# NewType — distinct types, the checker won't mix them up:
# RGB = NewType("RGB", tuple[int, int, int])
# HSL = NewType("HSL", tuple[int, int, int])
#
# class User(TypedDict):
#     first_name: str
#     last_name: str
#     age: int | None
#     email: str
#     fav_color: RGB | None
#
# Alias version of User with RGB (conflicts with the TypedDict above — pick one):
# type User = dict[str, str | int | RGB | None]
#
# def create_user(first_name: str, last_name: str, age: int | None = None, fav_color: RGB | None = None) -> User:
#     email = f"{first_name.lower()}_{last_name.lower()}@example.com"
#     return {
#         "first_name": first_name,
#         "last_name": last_name,
#         "age": age,
#         # "age": str_age,         # duplicate key — overwrote age, and broke the int | None type
#         "email": email,
#         "fav_color": fav_color,
#     }
#
# str_age = str(age)              # must live inside the function; `age` doesn't exist out here
#
# Plain tuple — runs, but the checker rejects it (a tuple is not an RGB):
# user1 = create_user("John", "Doe", age=38, fav_color=(109, 123, 134))
# user2 = create_user("Jane", "Doe", 40, fav_color=(132, 184, 104))
# user3 = create_user("Sam", "Lee")
#
# Wrapped in RGB(...) — correct:
# user1 = create_user("John", "Doe", age=38, fav_color=RGB((109, 123, 134)))
# user2 = create_user("Jane", "Doe", 40, fav_color=RGB((132, 184, 104)))
# user3 = create_user("Sam", "Lee")


# =============================================================================
#  v6 — FINAL (this code RUNS): dataclass + generics + type inference
# =============================================================================

# --- NewType (explained in v5) -----------------------------------------------
RGB = NewType("RGB", tuple[int, int, int])   # red, green, blue — each 0..255
HSL = NewType("HSL", tuple[int, int, int])   # hue, saturation, lightness — same shape, different meaning


# --- DATACLASS ----------------------------------------------------------------
#
#  LIKE YOU'RE 10:
#    `@dataclass` is a cookie cutter. You draw the shape once and Python builds
#    the machine that stamps out `User` objects. You get printing and
#    comparison for free, and you can write `user.email`. One rule: fields
#    without defaults must come first.
#
#  ENGINEER NOTES:
#    * @dataclass auto-generates __init__ (constructor), __repr__ (nice printing)
#      and __eq__ (compare two users with ==).
#    * Access fields with a DOT: user.email (TypedDict needs user["email"]).
#    * Defaults ARE allowed here (unlike TypedDict).
#    * RULE: fields WITHOUT defaults must come BEFORE fields WITH defaults,
#      or you get "TypeError: non-default argument follows default argument".
#      That's why `email` moved above `age`.
#    * Import is `from dataclasses import dataclass` (plural module, lowercase decorator).
#    * Don't combine @dataclass with TypedDict — pick one.
#    * For a list default use field(default_factory=list), never `= []`.
#
#  TypedDict vs dataclass vs Pydantic:
#    TypedDict  -> plain dict, user["x"], good for JSON you already have
#    dataclass  -> real object, user.x, defaults, good for your own app objects
#    Pydantic   -> like dataclass + RUNTIME VALIDATION, good for API input (FastAPI)

@dataclass
class User:
    first_name: str
    last_name: str
    email: str                      # no default -> must come before fields that have defaults
    age: int | None = None          # default value: None if not given
    fav_color: RGB | None = None    # must be an RGB (wrapped), or None


# --- GENERICS -----------------------------------------------------------------
#
#  LIKE YOU'RE 10:
#    Generics (`[T]`) are a magic grab bag. Put in marbles and a marble comes
#    out; put in candy and candy comes out. `Any` is a mystery bag: something
#    comes out, but nobody knows what it is anymore.
#
#  ENGINEER NOTES:
#    * T is a TYPE VARIABLE: a placeholder decided at each call.
#        random_choice(list[User]) -> returns User
#        random_choice(list[str])  -> returns str
#      The checker tracks it, so autocomplete works on the result.
#    * Four styles below (renamed so they don't overwrite each other —
#      in Python, defining the same function name twice keeps only the LAST one):

# 1. Old-style generic with TypeVar (works on Python 3.5+)
T = TypeVar("T")

def random_choice_typevar(items: list[T]) -> T:
    return random.choice(items)


# 2. New-style generic (Python 3.12+), RECOMMENDED — no TypeVar import needed.
#    TypeScript equivalent: function randomChoice<T>(items: T[]): T
def random_choice[T](items: list[T]) -> T:
    return random.choice(items)


# 3. Concrete type: only accepts a list of User, always returns User.
#    Fine when it truly only ever handles users; not reusable.
def random_user(items: list[User]) -> User:
    return random.choice(items)


# 4. Any: accepts anything, but the checker LOSES the type of the result.
#    Avoid unless you really can't describe the type.
def random_any(items: list[Any]) -> Any:
    return random.choice(items)


# --- THE FACTORY FUNCTION -----------------------------------------------------
#
#  LIKE YOU'RE 10:
#    create_user is a little factory. You hand it a first and last name
#    (and maybe an age and favorite color). It makes up an email address and
#    hands back a finished User cookie.
#
#  ENGINEER NOTES:
#    * Each parameter has a hint; `-> User` is the return type.
#    * f-string: f"{first_name.lower()}" drops variables into text.
#      Because first_name is hinted as str, the editor knows .lower() exists.
#    * Returns User(...) using KEYWORD arguments, so order mistakes are impossible.

def create_user(
    first_name: str,
    last_name: str,
    age: int | None = None,
    fav_color: RGB | None = None,
) -> User:
    email = f"{first_name.lower()}_{last_name.lower()}@example.com"
    return User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        age=age,
        fav_color=fav_color,
    )


# --- USING IT -----------------------------------------------------------------

user1 = create_user("John", "Doe", age=38, fav_color=RGB((109, 123, 134)))   # keyword arguments
user2 = create_user("Jane", "Doe", 40, fav_color=RGB((132, 184, 104)))       # age passed by position
user3 = create_user("Sam", "Lee")                                           # defaults: age and fav_color are None

print(user1)   # User(first_name='John', last_name='Doe', email='john_doe@example.com', age=38, fav_color=(109, 123, 134))
print(user2)
print(user3)   # ... age=None, fav_color=None

users = [user1, user2]                   # checker infers: list[User]
rando_user = random_choice(users)        # checker knows: User  (generic T = User)
print(rando_user)

# List comprehension: "for each user in users, grab user.email"
emails = [user.email for user in users]  # list[str] — dot access works because User is a dataclass
rando_email = random_choice(emails)      # SAME function, now checker knows: str  (T = str)
print(rando_email)


# =============================================================================
#  TYPE INFERENCE — the checker guesses types for you
# =============================================================================
#
#  LIKE YOU'RE 10:
#    Type inference is like a box whose first item was a toy car. Everyone
#    figures out it’s the car box. If you stuff a sock in later, the checker
#    says “that’s the car box!” Python itself lets you.
#
#  ENGINEER NOTES:
#    * You don't need to annotate every variable. The checker INFERS the type
#      from the first assignment: status = resp.status_code -> status: int.
#    * Reassigning to a different type (status = "ok") RUNS fine, but mypy /
#      Pylance flag "incompatible types in assignment".
#    * requests.get(url, timeout=5): sends an HTTP GET; timeout=5 means "give
#      up after 5 seconds" — always set a timeout in real code or it can hang forever.
#    * resp.status_code is the HTTP status number (200 = OK, 404 = not found).
#    * mypy needs `pip install types-requests` (requests has no built-in hints;
#      the stubs live in the typeshed project). Pylance already bundles them.
#    * TypeScript does the same: let status = 200; status = "ok"; -> error.

resp = requests.get("https://coreyms.com", timeout=5)
status = resp.status_code     # checker infers: status is int
print(status)                 # e.g. 200

status = "ok"                 # runs fine, but the checker flags it: str is not int
print(status)                 # ok

# Three ways to fix the warning above:
#
# 1. BEST — separate names for separate kinds of data:
# status_code = resp.status_code
# status_text = "ok"
#
# 2. Say up front that both types are allowed:
# status: int | str = resp.status_code
# status = "ok"
#
# 3. Keep ONE consistent type:
# status = str(resp.status_code)
# status = "ok"
