"""Generate a synthetic dataset of young people for the EYST attendance project.

All of the data produced here is FAKE/SYNTHETIC. The real EYST data never enters this
repository for safeguarding (see .gitignore and docs/data_protection.md)."""

import random
from datetime import date, timedelta

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
START_DATE = date (2025, 9, 3) # Wednesday: EYST drop-ins run on Wednesdays
NUM_SESSIONS = 40 # roughly a school year of weekly drop-ins

# Build one dictionary per young person, then convert to a table.
rows = []
#loop 100 times
for i in range(1, NUM_YP + 1):  # range stops before its end (100 exclusive), so +1 gives IDs 1 to 100
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

# Sessions table: one drop-in per week 
# Built from a dictionary of columns.
# The list comprehension adds one week to the start date for each session, so every session falls on a Wednesday.
sessions = pd.DataFrame({
    "session_id": range (1, NUM_SESSIONS + 1),
    "session_date": [START_DATE + timedelta(weeks=w) for w in range (NUM_SESSIONS)]
})

# Hidden attendance type 
# sets each person's weekly attendance probability so that the fake data contains realistic patterns.
# The weights are assumptions (not measured from EYST). The model must never use this column.
young_people["attendance_type"] = random.choices(
    ["regular", "occasional", "drifter"],
    weights = [0.25, 0.50, 0.25], # odds of each type, in the same order as the list
    k=NUM_YP, # one pick per young person
)

# Simulate attendance
# Every person is checked against every session (100 x 40 = 4,000 checks).
attendance_rows = []
for _, person in young_people.iterrows():
    for _, session in sessions.iterrows():
        week = session["session_id"] # used by the drifter formula below

        # Set the chance this person attends this week, based on their type
        if person["attendance_type"] == "regular":
            prob = 0.80
        elif person["attendance_type"] == "occasional":
            prob = 0.35
        else:
            # drifter: starts near 70% and fades to zero over the sessions
            prob = 0.7 * (1 - week / NUM_SESSIONS)

        # attendance table
        # Weighted coin flip: attend if a random number (0 to 1) is less than prob
        if random.random() < prob:
            minutes_late = random.randint(0, 120)
            # at 5pm drop-in runs till 7pm (2 hours - 120 minutes)
            attendance_rows.append({
                "young_person_id": person["young_person_id"],
                "session_id": session["session_id"],
                "minutes_after_start": minutes_late,
            })

# Sanity checks
attendance = pd.DataFrame(attendance_rows)
print(sessions.head())
print(attendance.head())
print("Total attendance records: ", len(attendance))
print(attendance.groupby("session_id").size().head())
print(sessions["session_date"].apply(lambda d: d.strftime("%A")).unique())

# Save the tables as CSV files 
# index=False stops pandas adding a row-number column.
# The hidden type is the answer key, not a real column, so it is dropped from young_people.csv and saved 
# separately to evaluate the model later.
young_people.drop(columns="attendance_type").to_csv("data/synthetic/young_people.csv", index=False)
young_people[["young_person_id", "attendance_type"]].to_csv("data/synthetic/ground_truth_types.csv", index=False)
sessions.to_csv("data/synthetic/sessions.csv", index=False)
attendance.to_csv("data/synthetic/attendance.csv", index=False)