Classes and Constructors (Real Python)
Dunder methods

Methods like .__init__() and .__str__() are called dunder methods because they begin and end with double underscores.

python
class Dog:
    species = "Canis familiaris"

    def __init__(self, name, age):
        self.name = name
        self.age = age

    # Instance method
    def description(self):
        return f"{self.name} is {self.age} years old"

    # Another instance method
    def speak(self, sound):
        return f"{self.name} says {sound}"
python
>>> miles = Dog("Miles", 4)

>>> miles.description()
'Miles is 4 years old'

>>> print(miles)
<__main__.Dog object at 0x00aeff70>
python
class Dog:
    # ...

    def __str__(self):
        return f"{self.name} is {self.age} years old"
python
>>> miles = Dog("Miles", 4)
>>> print(miles)
Miles is 4 years old




Claude i