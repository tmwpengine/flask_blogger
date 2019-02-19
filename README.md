A basic blogger written with the flask framework

# To install with pipenv
pipenv install --deploy

# Configure database
flask db migrate
flask db upgrade

# To Run
flask run
