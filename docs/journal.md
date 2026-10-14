# Project Journal

## Project context

EYST is a youth charity that currently records drop-in attendance on paper. This project builds a digital attendance register, a database fed by their registration form, and analytics and prediction of future attendance. Real data stays on EYST's systems. This repository contains only synthetic data.

## Entry 1: Setup

- Created the repository and added `.gitignore` rules for `data/raw/`, `data/real/`, `*.db` and `exports/` before introducing any data, so that real EYST data is protected and cannot accidentally reach GitHub.

- Created the following folder structure: `data/raw`, `data/synthetic`, `src`, `tests`, `docs`.

- Wrote the project documentation in Markdown, starting with `docs/journal.md`, so it renders on GitHub, sits next to the code, and has a full change history in Git.

- Decided to keep the database simple and minimise the data I store. The spreadsheet has a plethora of columns, like addresses and next of kin, but the attendance register doesn't need them. So I only kept what the register needs, which also means I'm not copying sensitive information about young people for no reason. This is called data minimisation.

- Set up an isolated Python virtual environment, installed pandas and faker using pip, and pinned my library versions in `requirements.txt`, so the project is reproducible on any machine. Chose pandas for cleaning the dataset and Faker for generating synthetic data, so real names are never needed in development following GDPR compliance by data minimisation.

## Entry 2: Design decisions

- Used synthetic data for the repository and the initial models, because the real data is about real young people and must never be public. Once the system is live, models could be retrained locally on real attendance data, which never leaves EYST's machine. Hand-written test cases with the cleaned result known will verify that the cleaning code for the dataset works, while the larger synthetic dataset will drive the dashboard and prediction model.

- Identified a gap in the initial design: young people who aren't registered are supposed to be directed to the QR code page but would have no way to record attendance for that session. Therefore, Added a "registration pending" walk-in option in the design that stores only name and time in, in a separate `walk_ins` table so the main young people table stays clean.

- Kept staff intervention minimal (matching how EYST currently runs -  paper register format). Young people enter their own name, and staff review walk-ins once before the file is saved. 

- Identified a second problem: young people might keep attending as walk-ins without ever registering. The system flags repeat unregistered walk-ins and prompts them to register, but never blocks attendance, for safeguarding reasons.

- Staff will check the total attendance on the Done screen before saving, as a sanity check on the count.

- Real attendance history only begins once the system is live, so the prediction model will train on synthetic data first. This limitation will be stated in the documentation.

## Entry 3: Synthetic data

- Built a seeded generator (`src/generate_synthetic.py`) that creates 100 fake young people with an ID, name, year of birth and photo consent. Seeding both `random` and Faker makes the output identical every time, so results are reproducible for anyone who clones the repo.
- Stored year of birth instead of exact date of birth, to stay in line with data minimisation.
