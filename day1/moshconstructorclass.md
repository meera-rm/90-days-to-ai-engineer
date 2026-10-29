 ---------- person.py ----------
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def talk(self):
        print(f"Hi there, I am {self.name}")

person = Person("John Doe", 40)
person.talk()
print(person.name, person.age)


# ---------- utils.py ----------
def find_max(numbers):
    maximum = numbers[0]
    for number in numbers:
        if number > maximum:
            maximum = number
    return maximum                      # return, don't print


# ---------- main.py ----------
from utils import find_max              # no ".py"
print(find_max([1, 34, 56, 75]))        # 75  (built-in: max(numbers))


# ---------- dice ----------
import random

class Dice:
    def __init__(self, sides_a=6, sides_b=6):
        self.sides = (sides_a, sides_b)

    def roll(self):
        a, b = self.sides
        return random.randint(1, a), random.randint(1, b)

print(Dice(10, 10).roll())              # e.g. (3, 8)


# ---------- pathlib ----------
from pathlib import Path
# absolute path = from root; relative path = from current dir
path = Path("emails")
path.mkdir(exist_ok=True)               # safe to re-run
for file in Path().glob("*"):           # everything in current dir
    print(file)
print(list(Path().glob("*.py")))        # just .py files


# ---------- openpyxl ----------
import openpyxl as xl
from openpyxl.chart import BarChart, Reference

def process_workbook(filename):
    wb = xl.load_workbook(filename)
    sheet = wb["Sheet1"]

    for row in range(2, sheet.max_row + 1):
        cell = sheet.cell(row, 3)
        if not isinstance(cell.value, (int, float)):   # skips blanks AND text
            continue
        sheet.cell(row, 4).value = cell.value * 0.9

    values = Reference(sheet, min_row=2, max_row=sheet.max_row,
                       min_col=4, max_col=4)
    chart = BarChart()
    chart.add_data(values)
    sheet.add_chart(chart, "E2")

    wb.save(filename.replace(".xlsx", "_updated.xlsx"))

process_workbook("transactions.xlsx")

Real-world engineering takeaways

Return values, don’t print them. Functions that return can be tested, reused, and composed in pipelines, while print-only functions are dead ends.
Make scripts idempotent. mkdir(exist_ok=True) and saving to _updated.xlsx instead of overwriting mean a rerun won’t crash or corrupt data. This is the same principle as rerunnable ETL jobs.
Validate input types, not just None. Real spreadsheets have stray text, so isinstance protects the job.
Generators are lazy. glob doesn’t read the whole directory up front, which matters when you scan large folders or S3-like listings.