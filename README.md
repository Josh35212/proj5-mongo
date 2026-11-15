# Project 5: Brevet time calculator with Ajax and MongoDB

*Author: Josh Gilliam*

*Email: jgilliam@uoregon.edu*

Simple list of control times from project 4 stored in MongoDB database.

## Completed Tasks

1. Created two buttons "Submit" and "Display" in the page where have control times.
2. On clicking the Submit button, the control times are entered into the database.
3. On clicking the Display button, the entries from the database arew displayed in a new page.

## Brevet Control Time Rules

Opening and closing times are calculated using the official ACP brevet calculator:
https://rusa.org/pages/acp-brevet-control-times-calculator

- Unit of measurment is Km, Miles is supported, but converted
- Opening times indicate the earliest arrival at a control
- Closing times indicate the latest arrival at a control
- Times are calculated based on the controls distance from the start
- Control times are displayed to the user as "WEEK-DAY Month/Day Hour/Minute"
  (EX: "Sun 1/1 1:30")
