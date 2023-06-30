#  Foodgram - "Food assistant"

## Technologies used
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=for-the-badge&logo=Docker&logoColor=white&color=008080)

##  Description
On this service, users will be able to publish recipes, subscribe to publications of other users,
add your favorite recipes to the "Favorites" list, and before going to the store, download a summary list
products needed to prepare one or more selected dishes.

### Main page
The content of the main page is a list of the first six recipes, sorted by publication date (newest to oldest).
The rest of the recipes are available on the following pages: there is pagination at the bottom of the page.

### Recipe page
The page contains the full description of the recipe. For authorized users - the ability to add a recipe to favorites and
to the shopping list, the ability to subscribe to the author of the recipe.

### User page
On the page - the username, all recipes published by the user and the ability to subscribe to the user.

### Subscribe to authors
Subscription to publications is available only to an authorized user. The subscriptions page is only available to the owner.

### Favorites list
Work with the list of favorites is available only to an authorized user.
The favorites list can only be viewed by its owner.

### Shopping list
Work with the shopping list is available to authorized users.
The shopping list can only be viewed by its owner.
The shopping list is downloaded in .txt format

### Filter by tags
Clicking on a tag name displays a list of recipes marked with that tag. Filtering is carried out on several
tags in the combination "or": if several tags are selected, the result will show recipes that are marked
at least one of these tags. When filtering on the user page, only the recipes of the selected user are filtered.
The same principle is observed when filtering the list of favorites.

### Registration and authorization
The system of registration and authorization of users is available in the project.

## Resources
- Resource **auth**: authentication.
- Resource **users**: users and subscriptions
- Resource **recipes**: recipes, tags, ingredients, featured recipes, shopping list
- Resource **api**: all functionality, only through api requests

### User roles and permissions
**What unauthorized users can do**
- Create an account
- View recipes on homepage
- View individual recipe pages
- View user pages
- Filter recipes by tags
- Work with a personal shopping list: add / delete any recipes, upload a file with the number of required
  ingredients for shopping list recipes

**What authorized users can do**
- Log in with your username and password
- log out (log out)
- Recover your password
- Change your password
- Create/edit/delete your own recipes
- View recipes on homepage
- View user pages
- View individual recipe pages
- Filter recipes by tags
- Work with a personal favorites list: add recipes to it or delete them,
  view your favorite recipes page
- Work with a personal shopping list: add / delete any recipes, upload a file with the number of required
  ingredients for shopping list recipes
- Subscribe to publications of recipe authors and unsubscribe, view your subscription page

## Peculiarities
The project runs in four docker-compose containers:
- **frontend** container of the frontend part of the JS-React project, will prepare the files necessary for the frontend application to work,
  and stop working
- **web** container for the Django application backend
- **nginx** container responsible for distributing statics
- **db** database container via postgres:13.0-alpine

## Preparing and launching the project
### Clone the repository
Clone the repository to your local machine:
```bash
git@github.com:Oleg-2006/foodgram-project-react.git
```

### Launching and working with the project
**Step 1** Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/Scripts/activate
```

**Step 2** Create an .env file with the touch .env command and add environment variables to it:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=f00dgram
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=<your_django_secret_key>
```
To ensure the safety of the project, after adding .env to `setting.py`, you must remove the *default* values ​​in the variables.

**Step 3** Update pip and install dependencies:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Step 4** Collect containers:
```bash
cd foodgram-project-react/infra
docker-compose up -d --build
```
Upon successful creation of containers in the terminal, the status should be:
```
    Status: Downloaded newer image for nginx:1.19.3
    Creating infra_db_1       ... done
    Creating infra_web_1      ... done
    Creating infra_nginx_1    ... done
```

**Step 5** Run migrations, collect statics and create superuser:
```bash
docker-compose exec -T web python manage.py makemigrations users --noinput
docker-compose exec -T web python manage.py makemigrations recipes --noinput
docker-compose exec -T web python manage.py migrate --noinput
docker-compose exec -T web python manage.py collectstatic --no-input
docker-compose exec web python manage.py createsuperuser
```
To populate the database with the initial data of the list of ingredients and tags, run:
```bash
docker-compose exec -T web python manage.py add_ingredients
docker-compose exec -T web python manage.py add_tags
```
Now you can go to the admin panel *http://<your host>/admin/* under your administrator login.

### Run a project on a remote server

**Step 1** Copy the following files and directories to the root of your home folder on the remote server
- `./docs/*`
- `./frontend/*`
- `./infra/docker-compose.yml`
- `./infra/nginx.config`
- `./infra/.env`

**Step 2** Edit the .env file in the root of the home folder on the remote server, fill in as shown
from .env file

**Step 3** Install docker according to the manual on the official website

**Step 4** Run the project with the command
```bash
docker-compose up -d --build
```
**Step 5** Inside the container create migrations, create superuser, collect statics, load tags and ingredients
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
docker-compose exec web python manage.py add_tags
docker-compose exec web python manage.py add_ingredients
```

## Specification
You can see the full API specification in the running project at http://localhost/api/docs/.

## Authors
- [Aleh Maslau](https://github.com/Oleg-2006)
