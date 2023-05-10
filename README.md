# Foodgram Rpoject
[![Foodgram workflow](https://github.com/ead3471/foodgram-project-react/actions/workflows/foodgram_workflow.yaml/badge.svg)](https://github.com/ead3471/foodgram-project-react/actions/workflows/foodgram_workflow.yaml)
## This is a Foodgram project -a special service for cooking enthusiasts.<br>
Users can:
- Register
- Publish their own recipes
- Subscribe to favorite authors
- Add recipes to favorites
- Add recipes to the shopping cart
- Download the shopping cart in PDF format with calculated total ingredients

## Current location:<br>
http://158.160.44.52/

API spec available at http://158.160.44.52/api/docs/

### Superuser Login

- Email: root@root.com
- Password: 1

## Local project deploy:<br>
1. Install Docker on your computer

2. Clone project from Github
```
git clone git@github.com:ead3471/foodgram-project-react.git
```

2. Navigate to the infra folder
```
cd foodgram-project-react/infra
```

4. Rename file '.env_example' to '.env' and correct values (you can leave everything as it is)
 ```
mv .env_example .env
nano .env
```

5. Run Docker images
 ```
 docker-compose -f docker-compose_local.yml up --build
 ```

 - Make migrations
```
docker-compose -f docker-compose_local.yml exec db sh
cd app
python manage.py migrate
```


6. Create superuser
```
python manage.py createsuperuser
```

7. (Optional) Load about 2000 ingredients into your database:
 ```
docker-compose -f docker-compose_local.yml exec db sh
```
 ```
 psql -U postgres
```
```
COPY recipes_ingredient FROM '/tmp/data/ingredients.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',', ENCODING 'UTF8');
```

## Remote project deploy:<br>
1. Clone project from github to your computer
```
git clone git@github.com:ead3471/foodgram-project-react.git
```

2. Navigate to the infra folder
```
cd foodgram-project-react/infra
```

3. Rename file .env_example to .env and correct values (you can leave everything as it is)

4. Connect to your server
 ```
ssh <server user>@<server IP>
```

5. Install docker on your server(depends on exact server os)

6. Create folder foodgram_setup on server
 ```
 mkdir foodgram_setup
 ```

7. From another cli copy infra, data and docs folder to the server 
 ```
 scp -r infra/* <server> <user>@<IP>:foodgram_setup
 ```

  ```
 scp -r docs/* <server> <user>@<IP>:foodgram_setup
 ```

  ```
 scp -r data/* <server> <user>@<IP>:foodgram_setup
 ```

8. In the server cli navigate to setup folder
  ```
cd foodgram_setup
 ```

9. Run docker-compose
```
sudo docker-compose up -d --build
 ```
10. Make migrations
```
docker-compose exec back sh
cd app
python manage.py migrate
```
11. Create superuser
```
python manage.py createsuperuser
```

12. (Optional) Load about 2000 ingredients into your database:
 ```
sudo docker-compose exec db sh
```
 ```
 psql -U postgres
```

```
COPY recipes_ingredient FROM '/tmp/data/ingredients.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',', ENCODING 'UTF8');
```


### The project includes a built-in GitHub Action that can automatically deploy images to the specified server on push actions. Follow the steps below to set it up:
1. Setup secret keys in your GitHub repository's settings:
-  DB_ENGINE

 - DB_HOST

 - DB_NAME

 - DB_PORT

 - DJANGO_SUPERUSER_EMAIL

 - DJANGO_SUPERUSER_PASSWORD

 - DJANGO_SUPERUSER_USERNAME

 - DOCKER_PASSWORD

 - DOCKER_USERNAME

 - HOST (your deploy server address)
 - PASSPHRASE (SSH passphrase for connection to the deploy server)
 - POSTGRES_PASSWORD
 - POSTGRES_USER
 - SSH_KEY (SSH passphrase for connection to the deploy server)
 - USER (your username on the deploy server)

2. Commit and push the changes to your GitHub repository. The GitHub Action will automatically deploy the images to the specified server on every push action.


### Backend Author:
 - Gubarik Vladimir


### Used technologies:
![Alt-Текст](https://img.shields.io/badge/python-3.7-blue)
![Alt-Текст](https://img.shields.io/badge/django-3.2.18-blue)
![Alt-Текст](https://img.shields.io/badge/djangorestframework-3.14.0-blue)
![Alt-Текст](https://img.shields.io/badge/docker-20.10.23-blue)
![Alt-Текст](https://img.shields.io/badge/nginx-1.21.3-blue)
![Alt-Текст](https://img.shields.io/badge/gunicorn-20.0.4-blue)