# toy-data-web-app

This is a toy example of a data web application built using a modern data tech stack

- **Github repository**: <https://github.com/dataxight/toy-data-web-app/>

## How to use

First, clone this repo
```
git clone git@github.com:dataxight/toy-data-web-app
```

Next, create the virtual environment with all dependencies.  This is done using Poetry, so make sure you have Poetry installed first
```
pip install poetry
```

Next, go into the directory where this repo has been cloned, and invoke Poetry to install necessary dependencies
```
cd toy-data-web-app
poetry update
```

Finally, to run the example
```
poetry run python src/foo.py
```

Taipy will start a web server and open a browser window to point to the web app.  By default, it will run on on http://127.0.0.1:8080

