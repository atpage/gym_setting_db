# gym_setting_db

This package sets up a database for boulders (i.e. problems) and ropes (i.e. routes) at a climbing gym.

The main intent is to allow setters to propose grades for a new set, and climbers to vote on the grades.

## Usage

Ensure DB_URL is set in your environment variables.  e.g.:

    $ export DB_URL='sqlite3:///tmp/routes.db'
    
For postgres, the value might look like:

    postgresql://USERNAME:PASSWORD@HOST:5432/DATABASE?sslmode=require

Once the package is working, a couple of basic functions can get you started:
* `create_tables()` will create the schema in the DB (but only what doesn't exist).
* `populate_tables()` will load some default values for colors and grades from CSV files.  This should only be run once.

The main tables are:
* `users`: This can be used to control logins of setters.
* `rope_routes`, `boulder_problems`: Details of climbs, e.g. color, setter, date.
* `rope_votes`, `boulder_votes`: Votes from climbers about the grades.

The grade tables (`valid_boulder_grades`, `valid_rope_grades`) are used to provide the sort order of different grades.
Alphabetically or numerically, '5.10+' would come before '5.8', for example, which is not correct.
So the `order` column in those tables defines how the difficulties actually progress.
