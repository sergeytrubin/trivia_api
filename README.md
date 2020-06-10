# Full Stack Trivia API Backend
### Project features

1. Display trivia questions:
    - Player can display all the questions
    - Player can display questions by category
2. Player is able to delete any question.
3. Player is able to create new question.
4. Player can search for question based on a text query string.
5. Play the quiz game:
 - Player have an option to randomize all questions
 - Player have an option to randomize question within specific category.


## Getting Started

### Frontend Dependencies

#### Installing Node and NPM

This project depends on Nodejs and Node Package Manager (NPM). Before continuing, you must download and install Node (the download includes NPM) from [https://nodejs.com/en/download](https://nodejs.org/en/download/).

#### Installing project dependencies

This project uses NPM to manage software dependencies. NPM Relies on the package.json file located in the `frontend` directory of this repository. After cloning, open your terminal and run:

$npm install

## Running Your Frontend in Dev Mode

The frontend app was built using create-react-app. In order to run the app in development mode use ```npm start```. You can change the script in the ```package.json``` file. 

Open [http://localhost:3000](http://localhost:3000) to view it in the browser. The page will reload if you make edits.<br>

$npm start


### Backend Dependencies

#### Python 3.8

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

$pip install -r requirements.txt


This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:

$psql trivia < trivia.psql


## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

Environment Variables to run the server are stored in ".flaskenv" file. Please make sure that python-dotnet module is instaled ($pip list)

$cat .flaskenv
FLASK_APP=flaskr
FLASK_ENV=development

Alternatively, it is possible to add flask variables by running:
$export FLASK_APP=flaskr
$export FLASK_ENV=development

To run the server:
$flask run


Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 


### API Reference
- The API is accessable on http://127.0.0.1:5000/

### Endpoints

#### GET '/categories'
- Request Parameters: None
- Example of response:



## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```