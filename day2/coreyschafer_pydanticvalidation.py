
# Pydantic Validation Example

from ast import pattern
from functools import partial
import json
from operator import gt

from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field, ValidationError,computed_field, HttpUrl, SecretStr, EmailStr, ValidationInfo, field_validator, model_validator
from datetime import UTC, datetime
from typing import Literal, Annotated

"""from pydantic import BaseModel, HttpUrl, ValidationError

class Job(BaseModel):
    title: str
    url: HttpUrl
    salary_lpa: float | None = None

try:
    Job(title="ML Intern", url="not a url")
except ValidationError as e:
    print(e)  # tells you exactly which field failed
"""

def create_user(username, email, age):
    if not isinstance(username, str):
        raise TypeError("Username must be a string")
    if not isinstance(email, str):
        raise TypeError("Invalid email format")
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")

    return {"username": username, "email": email, "age": age}


user1 = create_user("coreyms", "CoreyMSchafer@gmail.com", 38)
print(user1)

try:
    user2 = create_user("johndoe", None, "old")
    print(user2)
except TypeError as e:
    print(e)




class UserBasic(BaseModel):
    uid:Annotated[int, Field(gt=0)]
    username: Annotated[str, Field(min_length=3,max_length=20)]
    email: str
    age: Annotated[int, Field(ge=3, le=130)]

    verified_at: datetime | None = None
    bio: Annotated[str, Field(max_length=500)] = ""
    is_active:bool=True

    first_name: str | None = None
    last_name: str | None = None
    follower_count: int = 0
    full_name: str | None = None
    created_at: datetime = datetime.now()

user3 = UserBasic(uid="123",username="coreyms", email="CoreyMSchafer@gmail.com", age=38, full_name="corey Schafer", first_name="corey", last_name="Schafer"  )
print(user3)

try:
    user4 = UserBasic(username="johndoe", email=None, age="old")
    print(user4)
except ValidationError as e:
    print(e)

print(user3.model_dump_json(indent=2))

def add_http_scheme(url: str) -> str:
    if not url.startswith("http://") and not url.startswith("https://"):
        return f"http://{url}"
    return url

@computed_field
def full_name(self) -> str | None:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None
   

@computed_field
@property
def display_name(self) -> str | None:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None
    


@computed_field
@property
def follower_count_display(self) -> str:
        if self.follower_count > 10000:
            return f"{self.follower_count // 1000}k followers"
        

#adding constraints



class Comment(BaseModel):
    
    content: Annotated[str, Field(min_length=1, max_length=1000)]
    author_email: EmailStr
    likes:int=0
    created_at: datetime = Field(default_factory=partial(datetime.now, tz=UTC))

class BlogPostBasic(BaseModel):
    pid: int
    title: Annotated[str, Field(min_length=5, max_length=200)]
    content: Annotated[str, Field(min_length=10)]
    view_count: int = 0

    is_published: bool = False

    tags: list[str] = Field(default_factory=list)

    slug: Annotated[str, Field(pattern=r"^[a-z0-9-]+$")]

    #created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    created_at: datetime = Field(default_factory=partial(datetime.now, tz=UTC))

    author_id: str | int

    status: Literal["draft", "published", "archived"] = "draft"


post = BlogPostBasic(
    pid=1,
    title="Sample Post",
    content="This is the content of the post.",
    view_count=0,
    is_published=False,
    tags=[],
    created_at=datetime.now(tz=UTC),
    author_id="123",
    status="draft",
    slug="sample-post"
)

print(post)
print(post.model_dump_json(indent=2))


# special types in Pydantic

class UserWithValidators(BaseModel):
    uid:UUID = Field(default_factory=uuid4)
    username: Annotated[str, Field(min_length=3,max_length=20)]
    email: EmailStr
    age: Annotated[int, Field(ge=3, le=130)]
    password: SecretStr
    website: HttpUrl | None = None

    verified_at: datetime | None = None
    bio: Annotated[str, Field(max_length=500)] = ""
    is_active:bool=True

    full_name: str | None = None
    created_at: datetime = datetime.now()


# Field validators for User model
    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value    

    @field_validator("username")
    @classmethod
    def username_validator(cls, value: str) -> str:
        if not value.isalnum():
            raise ValueError("Username must be alphanumeric")
        return value


    @field_validator("website", mode="before")
    @classmethod
    def website_must_be_valid(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith("http"):
            raise ValueError("Website must be a valid URL")
        return value

    
user3 = UserWithValidators(username="CoreySchafer", email="CoreyMSchafer@gmail.com", age=38, password="12345678", full_name="corey Schafer", website="https://example.com")
print(user3)


print(f"secretvalue :{user3.password.get_secret_value()}")






#CUSTOM VALIDATORS

class UserRegistration(BaseModel):
  
    email: EmailStr
   
    password: SecretStr
    confirm_password: SecretStr
    website: HttpUrl | None = None

@field_validator("confirm_password", mode="after")
@classmethod
def passwords_match(cls, value: str, values: dict) -> str:
    if "password" in values and value != values["password"]:
        raise ValueError("Passwords do not match")
    return value

def passwords_match(self) -> "UserRegistration":
    if self.password.get_secret_value() != self.confirm_password.get_secret_value():
        raise ValueError("Passwords do not match")
    return self
try:
    user_reg = UserRegistration(email="test@example.com", password="secret123", confirm_password="secret123")
    print(user_reg)
except ValidationError as e:
    print(e)





#dictionary formatAutoconfig and alias

class BlogPost(BaseModel):
    pid: int
    title: Annotated[str, Field(min_length=5, max_length=200)]
    content: Annotated[str, Field(min_length=10)]
    view_count: int = 0
    author:UserWithValidators #Nested model
    is_published: bool = False

    tags: list[str] = Field(default_factory=list)

    slug: Annotated[str, Field(pattern=r"^[a-z0-9-]+$")]  

    #created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    created_at: datetime = Field(default_factory=partial(datetime.now, tz=UTC))

    author_id: str | int

    status: Literal["draft", "published", "archived"] = "draft"
    comments: list[Comment] = Field(default_factory=list)

post_data = {
    "pid": 1,
    "title": "Test Post",
    "content": "This is a test post.",
    "view_count": 0,
    "author": {"username": "CoreySchafer", "email": "CoreyMSchafer@gmail.com", "age": 38, "password": "12345678", "full_name": "corey Schafer", "website": "https://example.com"},
    "is_published": False,
    "tags": [],
    "slug": "test-post",
    "created_at": "2024-06-06T12:00:00Z",
    "author_id": 1,
    "status": "draft",
    "comments": [
        {"content": "Great post!", "author_email": "reader1@example.com", "likes": 3},
        {"content": "Thanks for sharing.", "author_email": "reader2@example.com", "likes": 0}
    ]
}




post=BlogPost(**post_data)





#Alias Name and Dual Names

class UserWithAlias(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    uid:UUID = Field(alias ="id",default_factory=uuid4)
    username: Annotated[str, Field(min_length=3,max_length=20)]
    email: EmailStr
    age: Annotated[int, Field(ge=3, le=130)]
    password: SecretStr
    website: HttpUrl | None = None

    verified_at: datetime | None = None
    bio: Annotated[str, Field(max_length=500)] = ""
    is_active:bool=True

    full_name: str | None = None
    created_at: datetime = datetime.now()



    user_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "CoreySchafer",
        "email": "CoreyMSchafer@gmail.com",
        "age": 38,
        "password": "12345678",
        "full_name": "corey Schafer",
        "website": "https://example.com"
    }

   

    user6 = UserWithAlias(**user_data)

    user7 = UserWithAlias.model_validate(user_data)
    print(user7.model_dump_json(indent=2, by_alias=True, include={"email", "username"}, exclude={"password"}))






#loading directly from json string


class UserAsStrict(BaseModel):
    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow",
                              #validate_assignment=True,
    frozen=True)
    uid:UUID = Field(alias ="id",default_factory=uuid4)
    username: Annotated[str, Field(min_length=3,max_length=20)]
    email: EmailStr
    age: Annotated[int, Field(ge=3, le=130)]
    password: SecretStr
    website: HttpUrl | None = None

    verified_at: datetime | None = None
    bio: Annotated[str, Field(max_length=500)] = ""
    is_active:bool=True

    full_name: str | None = None
    created_at: datetime = datetime.now()



    user_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "CoreySchafer",
        "email": "CoreyMSchafer@gmail.com",
        "age": 38,
        "password": "12345678",
        "full_name": "corey Schafer",
        "website": "https://example.com",
        "notes": "This is a note"
    }



    user8 = UserAsStrict.model_validate_json(json.dumps(user_data))
    print(user8.model_dump_json(indent=2, by_alias=True, include={"email", "username"}, exclude={"password"}))

    user8.email="newemail.com"

"""
Where validation should happen:

At the boundary — right where untrusted data enters your system (API request body, CLI args, file/DB read, env vars). Not scattered through internal functions.

Why there: once data crosses that boundary and gets validated into a typed model, everything downstream can trust the shape and types without re-checking. That's the whole point of your User/BlogPost models in this file — validate once at construction, then pass the object around with confidence. Internal functions calling each other shouldn't need defensive isinstance checks (like your hand-rolled create_user) — that's redundant work repeated everywhere instead of done once.

"42" into an int field:

Pydantic coerces it. In lax mode (the default), a numeric string like "42" is parsed into 42 (int) — it succeeds, no error. This is "coercion," not strict type matching.

If you want it to reject strings and require an actual int, you'd need strict=True (either on the model config or per-field via Field(strict=True)), at which point "42" raises a ValidationError instead of being coerced.


"""
