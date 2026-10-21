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

- Extended the generator with weekly Wednesday sessions (17:00-19:00), developed a hidden attendance type per young person (regular, occasional, drifter) which drives the attendance probability, and simulated the attendance with arrival times, so once we get to it the prediction model has realistic-style patterns to learn even on the synthetic data.

- Kept the hidden type out of `young_people.csv` and stored it separately as an answer key, because real data has no such column. The model will derive its own features from attendance records, so the label can't leak into the inputs.

- The type mix and attendance probabilities are assumptions, not measured from EYST. Results on synthetic data will show that the pipeline works, but not how well it will predict real attendance.

## Entry 4: Messy registration data

- Built a generator for a deliberately messy fake registration export (`.xlsx`) on to the synthetic dataset we generated that mimics the MS Forms real dataset. Ensured a relatively accurate imitation via inconsistent capitals and spacing, mixed date formats, duplicate sign-ups, blanks and placeholders, a duplicate Email heading, and columns the system does not use all .

- Decided which fields the app database imports, using an allow-list, and justified each one against what the register and model actually need:
  - **Kept:** completion time (becomes the registration date, and breaks ties between duplicate sign-ups), full name (needed for the attendance register and search), date of birth (reduced to year of birth, enough for age analysis), and things interested in (I will keep this column as a possible model feature. If I end up not developing this feature I will drop this column also).
  - **Dropped:** start time (no use), both Email columns and phone number (contact details the attendance register never uses or needs), address and postcode (identifying), ethnic group (special category data, not needed for attendance), next of kin and parent/guardian names (adults connected to children, a safeguarding risk to copy), medical information (sensitive, not needed), and both consent fields (photography and partner sharing). EYST's original spreadsheet remains the record of all of these.
  - Any column I haven't chosen is dropped by default, so an unexpected field in a future export cannot reach the database by accident. This limits what the app processes and stores (data minimisation for this tool); it does not change what EYST holds in its original spreadsheet, which remains the record of all dropped data.

- Gave this script its own random seed, separate from the generator, so the mess is reproducible and a change to one script doesn't silently alter the other's output.