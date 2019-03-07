# ireporter

<<<<<<< HEAD
[![Build Status](https://travis-ci.org/jkamz/ireporter.svg?branch=develop)](https://travis-ci.org/jkamz/ireporter) [![Coverage Status](https://coveralls.io/repos/github/jkamz/ireporter/badge.svg?branch=develop)](https://coveralls.io/github/jkamz/ireporter?branch=develop) [![Maintainability](https://api.codeclimate.com/v1/badges/3e33878d5311b00883bf/maintainability)](https://codeclimate.com/github/jkamz/ireporter/maintainability)
=======
[![Build Status](https://travis-ci.org/jkamz/ireporter.svg?branch=develop)](https://travis-ci.org/jkamz/ireporter)
>>>>>>> ft-add-redflag-record-164272428

## Initial Auth Endpoints
 - User Signup
 ```
  /api/auth/signup/
 ```
 - User Login
 ```
  /api/auth/login/
 ```
 - User Logout
  ```
   /api/auth/logout/
 ```
 - User Account Activation
  ```
   api/auth/activate/
 ```
 - User Account Activation Resend Email
  ```
   /api/auth/resend/
 ```
 - User Password Reset Eamil
  ```
   /api/auth/reset_password/
 ```
 - User Password Confirmation
  ```
   /api/auth/reset_password_confirm/
 ```
 - User Set Password
  ```
   /api/auth/change_password/
 ```
 - User Set Email
  ```
   /api/auth/change_email/
 ```

## Initial Others Endpoints
 - Api Docs
 ```
  /api/
 ```
 - Api Schema
 ```
  /api/schema/
 ```

## Local Development Setup
 - First Create python virtual env
 ```
  $ virtualenv -p python .venv
 ```
 - Install Requirements
 ```
  $ pip install -r api/requiremts.txt
 ```
 - Copy .env-example to .env and set config
 ```
  $ copy .env-example .env
 ```
 - Create postgres database
 ```
  $ sudo su postgres
  $ psql
  postgres=# CREATE USER django WITH PASSWORD 'password';
  postgres=# ALTER ROLE django SET client_encoding TO 'utf8';
  postgres=# ALTER ROLE django SET default_transaction_isolation TO 'read committed';
  postgres=# ALTER ROLE django SET timezone TO 'UTC';
  postgres=# CREATE DATABASE ireporter_db;
  postgres=# GRANT ALL PRIVILEGES ON DATABASE ireporter_db TO django;
  postgres=# \q
  $ exit
 ```
 - Run Server
 ```
  $ python api/manage.py runserver
 ```
