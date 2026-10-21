"""Create a deliberately MESSY, FAKE registration export for the EYST project.

Reads the clean CSV made by generate_synthetic.py and damages it on purpose.
It mimics an MS Forms Excel download so the cleaning pipeline can be built and
tested without any real data. Everything here is synthetic.
"""

import random
from datetime import date, datetime, timedelta

import pandas as pd
from faker import Faker

# Separate seeds from generate_synthetic.py, so the mess is reproducible
# without changing the clean data.
random.seed(7)
fake = Faker("en_GB")
Faker.seed(7)

NUM_DUPLICATES = 6  # people who accidentally submit the form twice

# Headings in the style of the real form: trailing colons and a repeated "Email".
# Many columns exist only because the real export has them; the cleaner must
# prove it discards them (data minimisation).
HEADERS = [
    "ID", "Start time", "Completion time", "Email", "Full Name:",
    "Phone Number:", "Date of Birth", "Email", "Ethnic group", "Address",
    "Postcode", "Things interested in", "Next of kin name",
    "Parent/guardian name", "Can EYST take your photo?",
    "Consent to share information with partner organisations",
    "Medical information",
]

INTERESTS = ["Football", "Art", "Gaming", "Cooking", "Music", "Trips"]


def messy_name(first, last):
    """Return the full name written in a random messy style."""
    full = f"{first} {last}"
    # choices returns a list of one item, so [0] takes the item out
    style = random.choices(
        ["normal", "upper", "lower", "spaces", "random_case"],
        weights=[0.4, 0.15, 0.15, 0.15, 0.15],
    )[0]
    # return ends the function at once, so no else is needed
    if style == "upper":
        return full.upper()
    if style == "lower":
        return full.lower()
    if style == "spaces":
        return f"  {first}   {last} "
    if style == "random_case":
        # coin flip per character gives names like aDaM sMiTh
        return "".join(c.upper() if random.random() < 0.5 else c.lower() for c in full)
    return full  # "normal" falls through to here: the clean name


def messy_dob(year):
    """Pick a random date in the given year, written in a random text format (or blank)."""
    if random.random() < 0.05:  # 5% of dates are left blank
        return None
    d = date(year, 1, 1) + timedelta(days=random.randint(0, 364))
    # three separate formats: 03/04/2010, 2010-04-03, 03 April 2010
    fmt = random.choice(["%d/%m/%Y", "%Y-%m-%d", "%d %B %Y"])
    return d.strftime(fmt)


def consent_answer(consent):
    """Return the form's fixed answer: Yes or No (no mess; the cleaner discards this column)."""
    return "Yes" if consent else "No"


def sometimes_missing(value):
    """Occasionally replace a value with a blank (4%) or "N/A" (3%)."""
    r = random.random()
    if r < 0.04:
        return None
    if r < 0.07:
        return "N/A"
    return value


def build_row(person):
    """Build one form submission as a list, in the same order as HEADERS."""
    # random start within 30 days of 1 Aug 2025; form takes 2-10 minutes
    start = datetime(2025, 8, 1, 9, 0) + timedelta(minutes=random.randint(0, 60 * 24 * 30))
    completed = start + timedelta(minutes=random.randint(2, 10))
    email = fake.email()  # stored so the second Email column can reuse it
    # Values are matched to HEADERS by POSITION, so the order must be identical.
    return [
        0,  # response number, filled in later once rows are sorted by time
        start,
        completed,
        email,
        messy_name(person["first_name"], person["surname"]),  # the young person's name
        sometimes_missing(fake.phone_number()),
        messy_dob(person["year_of_birth"]),
        random.choice([email, None]),  # second Email column: same or blank
        # Columns below are NOT used by the system. They exist because the real
        # export has them, and the cleaner must prove it discards them.
        random.choice(["White", "Asian", "Black", "Mixed", "Other"]),
        fake.street_address(),
        sometimes_missing(fake.postcode()),
        "; ".join(random.sample(INTERESTS, k=random.randint(1, 3))),
        fake.name(),  # next of kin: a throwaway fake adult
        sometimes_missing(fake.name()),  # parent/guardian: sometimes blank or N/A
        consent_answer(person["photo_consent"]),
        random.choice(["Yes", "No"]),  # partner-sharing consent: fixed answers
        random.choice(["None", "", "Asthma", "Nut allergy"]),
    ]


# Start from the clean fake people, so we know the correct answer
young_people = pd.read_csv("data/synthetic/young_people.csv")

# Everyone submits once, then 6 random people submit a second time
submissions = [person for _, person in young_people.iterrows()]
repeaters = young_people.sample(n=NUM_DUPLICATES, random_state=7)  # random_state = pandas seed
submissions += [person for _, person in repeaters.iterrows()]

rows = [build_row(person) for person in submissions]

# Order by completion time (row[2]) and number responses 1, 2, 3...
# This ID is a form response number, not a young person ID, as in the real export.
rows.sort(key=lambda row: row[2])
for number, row in enumerate(rows, start=1):
    row[0] = number

# A list of rows plus headings (not dictionaries) allows the duplicate "Email" heading
registrations = pd.DataFrame(rows, columns=HEADERS)
registrations.to_excel("data/synthetic/registration_export_messy.xlsx", index=False)

# Sanity checks
print(registrations.head())
print("Rows in messy export:", len(registrations))
print("Shape (rows, columns):", registrations.shape)
print("Expected after cleaning:", len(young_people))