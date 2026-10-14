"""Generate a synthetic dataset of young people for the EYST attendance project.

All of the data produced here is FAKE/SYNTHETIC. The real EYST data never enters this
repository for safeguarding (see .gitignore and docs/data_protection.md)."""

import random
import pandas as pd
from faker import Faker 

# Fixed the seeds so that anyone running this script gets identical data, so results
# in the README and docs are reproducible. Faker has its own random system,
# so it needs its own seed.
random.seed(42)
fake = Faker("en_GB")
Faker.seed(42)

# Size of the synthetic dataset (only affects the fake data)
NUM_YP = 100

# Build one dictionary per young person, then convert to a table.
rows = []
#loop 100 times
for i in range(1, NUM_YP + 1):  # range stops before its end (99), so +1 gives IDs 1 to 100
    rows.append({
            "young_person_id" : i, # This is a unique key as names alone could possibly collide
            "first_name": fake.first_name(),
            "surname": fake.last_name(),
            "year_of_birth" : random.randint(2008, 2013), # year only, not full DOB (data minimisation)
            "photo_consent": random.choice([True, False]),
    })

young_people = pd.DataFrame(rows)

# Sanity checks
print(young_people.head())
print(len(young_people))