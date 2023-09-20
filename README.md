## Setup
1. After cloning this repository, cd into it.
2. Set up virtual environment via ```python3 -m venv env``` 
3. Activate the virtual environment via ```source env/bin/activate```
4. If it's properly set up, ```which python``` should point to a python under api-skeleton/env.
5. Install dependencies via ```pip install -r requirements.txt```

## Starting local flask server
Under api-skeleton/src, run ```flask run --host=0.0.0.0 -p 8000```

By default, Flask runs with port 5000, but some MacOS services now listen on that port.

## Running unit tests
All the tests can be run via ```pytest``` under api-skeleton/tests directory.

## Code Structure
* src/app.py contains the code for setting up the flask app.
* src/endpoints/ contains the file for enpoints.
* src/models/ contains all the database model definitions files.
* src/helpers/ contains the helper functions used in this challenge.

* tests/test_modules/ contains all the files to test each api.