

# 🎬 Movie & Tv-Show Library


## Table of Contents

- [Intro](#intro)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation-and-setup)
    - [Getting started](#getting-started-from-step-1-to-7)
    - [Setting up TMDB api](#setting-up-tmdb-api-keys)
    - [Manual vs periodic data import](#manual-data-import)
    - [Setting up RabbitMQ](#setting-up-rabbitmq)
    - [Running Celery Beat and Worker](#start-celery-worker-and-beat)
    - [Scheduling Periodic Tasks](#scheduling-periodic-tasks)
- [Important Notes](#important-notes)
- [Usage Guide](#usage-guide)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)



<br>

(The idea of this project is to to build a user friendly interface with an extensive movie/series library   database.)

<br>

## Intro

A Django-powered Media Library (for Movies and Tv-Shows).<br>
Where users can browse, like, comment and manage their favorite media into a watchlist.<br>
The project includes a seamless **like/unlike system with AJAX**, ensuring real-time updates without page reloads.

Search for specific content and use a serie of filter to refine the search.
<br>
...


<br>
<br>


## Features



#### 🎥 Movie & Series Management

View the latest **movies** and **series** <br>

track what you watch, write a note about it with **watchlist**. <br>
Share your thought with other movie enthusiast **Comment section** onthe medias 

###  Authentication

**User registration & login** <br>
Secure authentication with Django’s built-in system

####  **Like / Unlike System**

AJAX-powered Like/Unlike (No page reload!) <br>
View all **liked content** on a dedicated page in the user’s profile




### 📃 User Dashboard

Display User's profile information
Link to user's watchlist, last activities, liked content. 


<br>
<br>



## 🛠️ Tech Stack

<br>

|         Technology                                 |         Purpose         |
| -------------------------------                    | ----------------------- |
| **Python (Django)**                                | Backend framework       |
| **JavaScript (AJAX, jQuery, fetch api)**           | Frontend interactivity  |
| **Bootstrap**                                      | Styling & UI Components |
| **PostgreSQL**                                     | Database                |
| **Rabbit-MQ**                                      | Message broker          |
| **Celery**                                         | worker & Beat receiver  |
| **Pillow module**                                  | image rendering         |


<br>
<br>

## Prerequisites

This project uses:
-  **Python 3.11.9** or higher
-  **django 5.1.4** 
-  **celery 5.4.0**
-  **RabbitMQ 4.0.7**

<br>




## **Installation and Setup**

<br>

### **Getting started** (from step 1 to 7)
Follow these steps to get the project up and running on your local machine.


### 1️⃣ Clone the Repository

<div align="left">

```sh
 git clone https://github.com/yourusername/movie-library.git
 cd movie-library
```
<br>
</div>

### 2️⃣ Create a Virtual Environment

<div align="left">

```sh
 python -m venv venv
 source venv/bin/activate  # On Windows/powershell: venv\Scripts\activate
```
<br>
</div>

### 3️⃣ Install Dependencies



```sh
 pip install -r requirements.txt
```


<br>


### 4️⃣ Set up PostgreSQL database

if in postgresql terminal (sudo -su postgres)


```sh

CREATE DATABASE <databasename>;
CREATE USER <username> WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE <databasename> TO <username>;
ALTER DATABASE <databasename> OWNER TO <username>;
GRANT CONNECT ON DATABASE <databasename> TO <username>;
\q
exit

```



#### In settings.py Replace this:

```sh
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### With this DB postgres setup

```sh
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

```

#### store the credentials in the .env file

```sh

DB_NAME = "your_db_name"
DB_USER = "your_db_user_name"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = 5432

```


<br>


### 5️⃣ Create a Superuser <small>(Optional but recommended, for Admin Panel)</small>


```sh
 python manage.py createsuperuser
```
<br>



### 6️⃣ Apply Migrations


```sh
 python manage.py makemigrations

 python manage.py migrate
```
<br>


### 7️⃣ Run the Development Server


```sh
 python manage.py runserver
```
<br>


From now the web application should be working, but with no data population yet...<br>
Open [**http://127.0.0.1:8000/**](http://127.0.0.1:8000/) in your browser.

<br>
<br>



### **8️⃣ To import movies and tv shows data into the database:**


#### **Setting up TMDB API Keys**

This project is, set to and requires API keys from **The Movie Database (TMDB)**, to fetch movie and series data.<br>
You will therefore need an account on their website to use the implemented import feature.<br> 
For this: <br>

* Register on their website 'https://www.themoviedb.org/signup' <br>
* request to get an Api and read access key form your account setting<br>
* Store the Api Key and the Read Access Key in your **.env** file<br>


<br>
The import_data/api_services/ already have a TMDB directory with a Class that is called to authenticate the user when api calls are made via said import commands.


<br> 

#### **Manual data import**

<br>

**you can either import content manually** <small>(Not preferred method, but good for starting and testing)</small> 



by running files that are recognized by django as class management command<br> 
in using the class Basecommand from django module<br>
Placed in following the directory:<br>

```sh
 import_data/management/commands/...
```
 
 <br>

example to run a file named **import_tmdb_movies.py** <br>
(this should import new Movies object into the database)<br>

```sh
 python manage.py import_tmdb_movies
```

<br>

#### **Or you can set Tasks to automatically import content** <br>

by periodically running command tasks. To do so follow the next steps:

<br>

To install using pip (it should be already installed from earlier in 3) installing dependencies:

```sh
pip install -U Celery
```

<br>



#### **Setting up RabbitMQ**

This project uses RabbitMQ as the message broker for Celery.

1.  **Install RabbitMQ:**
    * Visit the official RabbitMQ website ([https://www.rabbitmq.com/download.html](https://www.rabbitmq.com/download.html)) and follow the installation instructions for your operating system (Windows, macOS, Linux).
    * On Windows, the installer from the official website is the recommended method.

<br>

2.  **Start RabbitMQ Service:**
    * After installation, ensure the RabbitMQ service is running.
    * On Windows, you can usually start the service from the Services Manager or by using the following command in an administrative command prompt:
        ```bash
        rabbitmq-service.bat start
        ```
    * Refer to the RabbitMQ documentation for startup commands on other operating systems.

<br>

3.  **Enable the RabbitMQ Management Plugin (Optional but Recommended):**
    * The management plugin provides a web interface for monitoring and managing your RabbitMQ instance.
    * Open a command prompt and navigate to the RabbitMQ `sbin` directory (e.g., `C:\Program Files\RabbitMQ Server\rabbitmq_server-<version>\sbin`).
    * Run the following command:
        ```bash
        rabbitmq-plugins enable rabbitmq_management
        ```
    * You can then access the management interface in your web browser at `http://localhost:15672/`.
    * It is then strongly recommended to create a new user with a new password and to remove the permissionsfrom the default guest user 



<br>


4.  **Check the status of RabbitMQ**


```
rabbitmqctl status
```

and otherwise to start the service with:


```
rabbitmq-service start
```

<br>



####  **Start Celery Worker and beat:**

Open two other separate terminals and navigate to your project's root directory.
With your virtual environment activated and the necessary libraries pre installed earlier.

1- Open a new command prompt or terminal window and navigate to your project's root directory.<br>

Run the following command:<br>
    ```
    celery -A movie_gen beat --loglevel=debug
    ```

<br>

On the other, run the following command:<br>
    ```
    start "Celery Worker" cmd /k "celery -A movie_gen worker --loglevel=info -P solo -E"
    ```

<br>
(This command starts a single Celery worker using the `solo` concurrency pool, with event monitoring enabled (`-E`). Youcan run more workers if needed by omitting the `-P solo` flag or using a differentpool.)*


<br>
<br>

**Note:** Ensure that your `movie_gen` package is correctly identified as your Celery app in your project's `celery.py` file. Your Celery tasks should be located in `import_data.tasks`.




#### Set periodic task with django admin panel

1.  **Access the Django Admin:**
    * Open your web browser and go to `http://127.0.0.1:8000/admin/`.
    * Log in with the superuser credentials you created.

2.  **Schedule Tasks:**
    * In the Django admin, find the "periodic tasks" section"
    * Click "Add periodic task" to create a new scheduled task.
    * **Schedule:** Choose the desired schedule type (e.g., Interval, Crontab) and configure the frequency.
    * **Task:** Enter the name of your Celery task function (e.g., `import_data.tasks.import_tmdb_movies_task`).
    * **Enabled:** Make sure the "Enabled" checkbox is selected.
    * Click "Save."

    * Celery Beat will now periodically check the database for scheduled tasks and send them to the Celery worker for processing.



<br>
<br>





---

## Usage Guide

<br>

## Future Improvements

<br>

Implement **API** to extend catalogues content. <br>

 search functionality (querying the database with **filtering options**) <br>
**Available on:** 
- Add a **watchlist** form to categorize as pop up menu form<br> 
- Add length filter to the filter search feature (possibly country or languages too)<br> 
- Pages link for short movies, animee or other genre just like documentaries<br> 
- Add an actor/creator and production class (will allow to search content through specific people).

- **where available** Get 3rd party platforms where contents are available for watching (eg: netflix, hbo...) 
- Implement **like analytics** for most liked content<br>
- **Recomendation** features <br>



<br>
<br>



## Contributing

<br>

Want to contribute? Fork the repo and submit a PR!


```sh
git checkout -b feature-branch
```

<br>


## License 


<br>

This project is **open-source** under the MIT License.

<br>

This [website, program, service, application, product] uses TMDB and the TMDB APIs but is not endorsed, certified, or otherwise approved by TMDB.

9️⃣🔟