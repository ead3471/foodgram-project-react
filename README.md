# Foodgram Rpoect
[![Foodgram workflow](https://github.com/ead3471/foodgram-project-react/actions/workflows/foodgram_workflow.yaml/badge.svg)](https://github.com/ead3471/foodgram-project-react/actions/workflows/foodgram_workflow.yaml)
## This is a Foodgram project -a special service for cooking enthusiasts.<br>
Users can:
 - register
 - publish their own recipes
 - subscribe to favorite authors
 - add recipes to favorites
 - add recipes to shopping cart
 - download shopping cart in PDF format with calculated total ingredients

## Current location:<br>
http://158.160.44.52/

APO spec available at http://158.160.44.52/api/docs/

## Local project deploy:<br>
 - Install docker on your computer

 - Clone project from github
```
git clone git@github.com:ead3471/foodgram-project-react.git
```

 - navigate to the infra folder
```
cd foodgram-project-react/infra
```

 - rename file .env_example to .env and correct values (you can leave everything as it is)
 ```
mv .env_example .env
nano .env
```

 - run docker images
 docker-compose -f docker-compose_local.yml up --build

 - you can add load about 2000 ingredients to you db
 ```
docker-compose -f docker-compose_local.yml exec -it db sh
```
 ```
 psql -U postgres
```
```
COPY recipes_ingredient FROM '/tmp/data/ingredients.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',', ENCODING 'UTF8');
```

## Remote project deploy:<br>
 - Clone project from github to your computer
```
git clone git@github.com:ead3471/foodgram-project-react.git
```

 - navigate to the infra folder
```
cd foodgram-project-react/infra
```

 - rename file .env_example to .env and correct values (you can leave everything as it is)

  - Connect to your server
 ```
ssh <server user>@<server IP>
```

 - Install docker on your server(depends on exact server os)

 - Create folder foodgram_setup on server
 ```
 mkdir foodgram_setup
 ```

 - from another cli copy infra folder to the server 
 ```
 scp -r infra/* <server> <user>@<IP>:foodgram_setup
 ```

 - in the server cli navigate to setup folder
  ```
cd foodgram_setup
 ```

 - run docker-compose
```
sudo docker-compose up -d --build
 ```

 - also you can add load about 2000 ingredients to you db
 ```
sudo docker-compose exec -it db sh
```
 ```
 psql -U postgres
```

```
COPY recipes_ingredient FROM '/tmp/data/ingredients.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',', ENCODING 'UTF8');
```

- Enjoy!






### Backend Author:
 - Gubarik Vladimir


### Used technologies:
![Alt-Текст](https://img.shields.io/badge/python-3.7-blue)
![Alt-Текст](https://img.shields.io/badge/django-3.2.18-blue)
![Alt-Текст](https://img.shields.io/badge/djangorestframework-3.14.0-blue)
![Alt-Текст](https://img.shields.io/badge/docker-20.10.23-blue)
![Alt-Текст](https://img.shields.io/badge/nginx-1.21.3-blue)
![Alt-Текст](https://img.shields.io/badge/gunicorn-20.0.4-blue)