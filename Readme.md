# StarterKitCloud - Backend

![alt text](http://www.starterkit.cloud/static/img/starter-kit-graphic.ab49944.png "Logo Title Text 1")

## everything you need to start your project

### general overview

To put it in to basic terms StarterKit is a project template. Starter Kit is a collection of useful open source tech that has been configured to work smoothly together. Everything a typical project needs is broken down in to manageable micro services that are easily deployable to any infrastructure that has docker installed. If you are starting from scratch this is a great starting point because it eliminates a lot of the grunt work required to start building the actual features that you need. Below is a breakdown of each micro service and the power it gives you.

| service        | purpose           |
| ------------- |:-------------:|
| web     | serves as an api where you make the endpoints that you need. It is using [django rest framework](http://www.django-rest-framework.org/) along with [django oauth toolkit](https://github.com/jazzband/django-oauth-toolkit). |
| rabbit      | A [rabbitmq](https://www.rabbitmq.com/) server with a management dashboard at port 15672 that gives you a detailed look in to your queue      |
| worker | This is a [celery](http://www.celeryproject.org/) worker process that consumes all of the jobs that are in the rabbit "default" queue |
| beat | This executes your scheduled tasks using [celery beat](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html) and puts your jobs in the rabbit "beat" queue |
| periodic_worker | this is a celery worker process that consumes all of the jobs that are in the rabbit "beat" queue|
| db | a [postgresql](https://www.postgresql.org/) service to use during local  development. Not meant to be used in production. It is better and easier to use something like amazon RDS for production.   |

## Get started:

First things first. You need to make a seed.env file that will hold all the credentials that the services will need to run.

The following can be used for a development environment. Of course you would use real credentials in production. * indicates a variable you need to set up with your own info. save the follwing as seed.env and place in the root of this repository.
```
DJANGO_SECRET_KEY=$3cr3t_k3y
DJANGO_DB=app_dev
DJANGO_DB_PASS=thepassword
DJANGO_DB_USER=app_dev
DJANGO_DB_HOST=db
DJANGO_S3_STORAGE=an-s3-bucket-for-static-files*
AWS_SECRET_ACCESS_KEY=aws-user-secret-key-that-has-s3-access*
AWS_ACCESS_KEY_ID=aws-user-key-that-has-s3-access*
CELERY_USER=rabbit
CELERY_PASSWORD=rabbitpass
CELERY_HOSTNAME=rabbit
RABBITMQ_DEFAULT_USER=rabbit
RABBITMQ_DEFAULT_PASS=rabbitpass
RABBITMQ_DEFAULT_VHOST=/

```


## Get started with the API
Run the following command to get started

`docker-compose up db web`

This will start up the database and the web application. You can now visit <http://localhost:8000> and you will see that django rest frame work is installed and running. [Learn more about django rest framework here.](http://www.django-rest-framework.org/)

### django management commands

Run your django migrations:

`docker-compose run web python ./manage.py migrate`

Create a super user:

`docker-compose run web python ./manage.py createsuperuser`

You can now log in to the API's admin area by visiting the following url in a browser <http://localhost:8000/admin> and logging in with the superuser you just created.

To see the running docker container:

`docker-compose ps`

You should see that 2 containers are running; db and web .


## Get started with rabbitMQ and Celery
In basic terms, celery is a python library that makes it easy to manage a queue of tasks in a scalable way. It is great for doing computing jobs that may take a long time or are just more convenient to do outside of the web application layer in general . [Learn more about celery here.](http://docs.celeryproject.org/en/latest/index.html)

In general it works like this:

send job to queue ---> rabbitMQ (broker that manages queue of jobs) ---> celery workers sit there waiting to do the jobs in the queue.


### regular tasks (demo)

**Stop all the services if you have any running.**

run the following command to start up celery "default" worker, rabbitMQ server, and web:

`docker-compose up rabbit worker web`

You can now visit <http://localhost:15672> in your browser and log in with

username: rabbit

password: rabbitpass

now run the test task:

There is a management command at <https://github.com/starterkitcloud/sk-backend/blob/master/app/sk_accounts/management/commands/example_task_command.py> called example_task_command .

Run the following command in another terminal:

`docker-compose run web python ./manage.py example_task_command`

You should see 1000 tasks print to screen from the worker service. Also, take a look at the rabbit dashboard and you will see that the queue stats change.

### run periodic tasks (demo):

**Stop all the services if you have any running.**

There is a periodic task scheduled in the settings at <https://github.com/starterkitcloud/sk-backend/blob/master/app/app/settings.py#L175-L186> called test_beat .

run the following command to start up celery "beat" worker, beat service, and rabbitMQ server:

`docker-compose up  periodic_worker beat rabbit`  

you should see the periodic_worker service print to screen every second.


### putting it all together

To run all the services at the same time all you have to do is this:

`docker-compose up`

Depending on what you are working on you usually don't need to run all the services at once outside of production.
