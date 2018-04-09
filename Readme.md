#This repository is responsible for providing a rest api and also handles worker processes
##get started with the API
run the following command to get started
docker-compose up db web

open another terminal and run the following command:
docker-compose run web python ./app/manage.py migrate

create a super user
docker-compose run web python ./app/manage.py createsuperuser

You can now log in to the API's admin area by visiting the following url in a browser http://localhost:8000/admin


General Overview:

To put it in to basic terms Starter Kit is a project template. Starter Kit is a collection of useful open source tech that has been configured to work smoothly together. Everything a typical project needs is broken down in to manageable micro services that are easily deployable to any infrastructure that has docker installed. If you are starting from scratch this is a great starting point because it eliminates a lot of the grunt work required to start building actual features. Below is a breakdown of each micro service and the power it gives you.
