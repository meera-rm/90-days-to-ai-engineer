
 The Core Testing Pattern

To test a model, pass valid data to verify it instantiates correctly, and pass invalid data to assert that it raises a ValidationError.
python
import pytest
from pydantic import BaseModel, EmailStr, Field, ValidationError

# 1. Define the model to test
class UserProfile(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    age: int = Field(..., ge=18)

# 2. Test valid data (Happy Path)
def test_user_profile_valid():
    valid_data = {
        "username": "johndoe",
        "email": "john@example.com",
        "age": 25
    }
    user = UserProfile(**valid_data)
    
    assert user.username == "johndoe"
    # Pydantic preserves correct types
    assert isinstance(user.age, int) 

# 3. Test invalid data (Error Path)
def test_user_profile_invalid_age():
    invalid_data = {
        "username": "johndoe",
        "email": "john@example.com",
        "age": 16  # Underage!
    }
    
    # Assert that ValidationError is raised
    with pytest.raises(ValidationError) as exc_info:
        UserProfile(**invalid_data)
    
    # Verify the specific error details
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("age",)
    assert "greater than or equal to 18" in errors[0]["msg"]
Use code with caution.

2. Testing Custom Validators

If your models use @field_validator or @model_validator, write dedicated test cases to verify their specific logic.
python
from pydantic import field_validator, model_validator

class Product(BaseModel):
    name: str
    price: float
    discount_price: float

    @field_validator("name")
    @classmethod
    def name_must_be_capitalized(cls, v: str) -> str:
        if not v.istitle():
            raise ValueError("Name must be capitalized")
        return v # Remember to always return the value!

    @model_validator(mode="after")
    def check_discount(self):
        if self.discount_price >= self.price:
            raise ValueError("Discount price must be less than the regular price")
        return self

# Test the field validator
def test_product_name_validation():
    with pytest.raises(ValidationError) as exc_info:
        Product(name="iphone", price=999, discount_price=799)
    assert "Name must be capitalized" in str(exc_info.value)

# Test the model validator
def test_product_discount_validation():
    with pytest.raises(ValidationError) as exc_info:
        Product(name="iPhone", price=500, discount_price=600)
    assert "Discount price must be less than the regular price" in str(exc_info.value)
Use code with caution.

3. Advanced Strategy: Snapshot Testing

For complex models with large schemas, writing manual dictionary assertions gets tedious. Pydantic teams heavily utilize inline-snapshot to manage complex data structures.
First, install the package: pip install inline-snapshot
python
from inline_snapshot import snapshot

def test_complex_model_serialization():
    user = UserProfile(username="alice", email="alice@example.com", age=30)
    
    # Dump the model to a built-in dict format
    # Leave snapshot() empty initially; run `pytest --inline-snapshot=fix` 
    # to let the library auto-populate the exact structure below.
    assert user.model_dump() == snapshot({
        'username': 'alice',
        'email': 'alice@example.com',
        'age': 30
    })
Use code with caution.

4. Integration Testing (FastAPI Example)

When testing routes that take Pydantic models as payloads, use FastAPI's TestClient to assert HTTP statuses (200 vs 422 Unprocessable Entity).
python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.post("/user")
def create_user(user: UserProfile):
    return {"status": "created"}

client = TestClient(app)

def test_fastapi_pydantic_integration():
    # Valid payload -> 200 OK
    response = client.post("/user", json={"username": "bob", "email": "bob@example.com", "age": 22})
    assert response.status_code == 200

    # Invalid payload -> 422 Unprocessable Entity
    response = client.post("/user", json={"username": "bob", "email": "not-an-email", "age": 22})
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error"



When testing Pydantic models, you should verify two primary behaviors: successful data instantiation (good values) and the correct fallback and validation of fallback behavior (default values).
Because Pydantic handles type coercion and schema structure out of the box, your tests should focus on ensuring your configurations, constraints, and default_factory methods behave exactly as your business logic requires.

1. Testing "Good" Values

When testing valid data, you want to ensure that the model instantiates properly and correctly coerces or maps inputs into the expected types.
python
import pytest
from pydantic import BaseModel, EmailStr

class UserProfile(BaseModel):
    username: str
    email: EmailStr
    age: int

def test_user_profile_good_values():
    # Arrange valid input data
    data = {
        "username": "johndoe",
        "email": "john@example.com",
        "age": "30"  # Pydantic will coerce this string to an int
    }
    
    # Act
    user = UserProfile(**data)
    
    # Assert
    assert user.username == "johndoe"
    assert user.email == "john@example.com"
    assert user.age == 30  # Verified successful coercion
Use code with caution.

2. Testing Default Values

Testing defaults means verifying both that omission works correctly and that mutable defaults don't bleed into other instances.

The Crucial Catch: Validation of Defaults

By default, Pydantic does not run validators on default values. If you have a custom validator or strict constraint, an invalid default won't crash until you trigger it or enforce it using validate_default=True.
python
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class Product(BaseModel):
    name: str
    # Use default_factory for dynamic values (like timestamps) or mutable objects (lists/dicts)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Enforce validation on the default value itself
    status: str = Field(default="active", validate_default=True)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ["active", "inactive"]:
            raise ValueError("Invalid status")
        return v

def test_product_defaults():
    # Act: Instantiate with only the required fields
    product = Product(name="Laptop")
    
    # Assert
    assert product.status == "active"
    assert isinstance(product.created_at, datetime)
Use code with caution.

3. Testing Bad Values (The Robustness Check)

Opinions are occasionally mixed on Stack Overflow regarding whether testing invalid inputs is testing your code or Pydantic itself. However, checking that your data boundaries throw a ValidationError ensures your field constraints (like gt, le, or custom validators) remain intact during refactors.
python
from pydantic import ValidationError

def test_product_invalid_values():
    # Act & Assert: Ensure ValidationError is raised for bad data
    with pytest.raises(ValidationError) as exc_info:
        Product(name="Bad Product", status="invalid_status")
    
    # Optional: Verify the specific error message location
    assert "Invalid status" in str(exc_info.value)
Use code with caution.

Quick Reference: Best Practices for Model Tests


Objective	Strategy	What to Look For
Data Coercion	Pass compatible types (e.g., "10" for an int)	Verify the final type is correct.
Dynamic Defaults	Use Field(default_factory=...)	Avoid created_at=datetime.now() (sets a fixed time at module load).
Mutable Defaults	Use Field(default_factory=list)	Avoid tags=[] (shares the exact same list across instances).
Constraint Validation	Use Field(validate_default=True)	Ensures bad defaults break early during startup or unit testing.

5. API-Level Equivalents (FastAPI TestClient)

The same three things you test on a bare model — good values, defaults, bad
values — you also test at the API layer, just through HTTP status codes and
response bodies instead of Python exceptions. Use `TestClient`, which calls
your app in-process (no running server needed).

python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr, Field

class UserProfile(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    age: int = Field(..., ge=18)

app = FastAPI()

@app.post("/users")
def create_user(user: UserProfile):
    return user

client = TestClient(app)

# Good values -> 200, and the response body reflects coercion/validation
def test_api_good_values():
    response = client.post("/users", json={
        "username": "johndoe",
        "email": "john@example.com",
        "age": "30",  # FastAPI/Pydantic coerces this the same as a bare model
    })
    assert response.status_code == 200
    assert response.json()["age"] == 30

# Defaults -> fields you omit should come back as the model's default
def test_api_defaults():
    response = client.post("/users", json={
        "username": "johndoe",
        "email": "john@example.com",
        "age": 25,
    })
    body = response.json()
    assert body["username"] == "johndoe"
    # if UserProfile had e.g. `status: str = "active"`, you'd assert:
    # assert body["status"] == "active"

# Bad values -> 422 Unprocessable Entity, not a Python ValidationError
def test_api_bad_values():
    response = client.post("/users", json={
        "username": "jo",       # too short, violates min_length=3
        "email": "not-an-email",
        "age": 16,               # violates ge=18
    })
    assert response.status_code == 422
    errors = response.json()["detail"]
    fields_with_errors = {tuple(e["loc"]) for e in errors}
    assert ("body", "username") in fields_with_errors
    assert ("body", "age") in fields_with_errors
Use code with caution.

Key differences from testing the model directly:
• You assert on `response.status_code` (422) instead of catching
  `ValidationError` with `pytest.raises`.
• The error list lives at `response.json()["detail"]`, and each entry's
  `loc` is prefixed with `"body"` (or `"query"`/`"path"` for those parameter
  types) since FastAPI reports where in the request the bad data came from.
• A single bad request can fail multiple fields at once — check the whole
  `detail` list rather than assuming one error.

If you'd like to tailor your tests further, tell me:
• What specific custom validators or constraints are you trying to test?
• Are you working with nested Pydantic models or co