# Project Journal

## Entry 1: Setup

- Created the repository and added `.gitignore` rules for `data/raw/`, `data/real/`, `*.db` and `exports/` before introducing any data, so that real EYST data is protected and cannot accidentally reach GitHub.

- Created the following folder structure: `data/raw`, `data/synthetic`, `src`, `tests`, `docs`.

- Decided to keep the database simple and minimise the data I store. The spreadsheet has a plethora of columns, like addresses and next of kin, but the attendance register doesn't need them. So I only kept what the register needs, which also means I'm not copying sensitive information about young people for no reason. This is called data minimisation.