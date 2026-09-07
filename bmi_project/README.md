# Overview

As a software engineer, I wanted to practice building a dynamic, multi-page web application using a backend framework instead of only static HTML. This project let me learn how a Python web framework (Django) receives a request, runs logic in a view function, and returns a page built from a template with real data plugged into it.

This is a BMI (Body Mass Index) Calculator web app. The user enters their height and weight on the home page, and the app calculates their BMI, shows which weight category they fall into, and offers a page of health tips tailored to that category.

To run the project on your own computer:
1. Install Django: `pip install django`
2. From the `bmi_project` folder, run: `python manage.py runserver`
3. Open a web browser and go to `http://127.0.0.1:8000/`

My purpose in writing this software was to learn how Django routes URLs to view functions, how data submitted by a user flows into Python code, and how that data can be used to dynamically build different HTML pages.

[Software Demo Video](http://youtube.link.goes.here)

# Web Pages

**Home page (`/`)** – Displays a form asking for height (cm) and weight (kg). Submitting the form sends the values to the Result page.

**Result page (`/result/`)** – Reads the height and weight from the submitted form, calculates the BMI, and dynamically displays the BMI number and category (Underweight, Normal weight, Overweight, or Obese). If the input is missing or invalid, it dynamically displays an error message instead. From here the user can go to the Tips page or return to the Home page.

**Tips page (`/tips/`)** – Dynamically generates a list of health tips based on which BMI category was passed in from the Result page, so the content changes depending on the user's result.

# Development Environment

I used Visual Studio Code as my editor, along with the Django web framework (version 6.1) for Python. I tested the app locally using Django's built-in development server and `curl` from the terminal to confirm each page and calculation worked correctly before viewing it in a browser.

# Useful Websites

* [Django Documentation](https://docs.djangoproject.com/en/5.0/)
* [Django Getting Started with Views](https://docs.djangoproject.com/en/5.0/intro/tutorial01/)
* [Django Template Language Overview](https://docs.djangoproject.com/en/5.0/ref/templates/language/)

# Future Work

* Add a metric/imperial unit toggle so users can enter height in feet/inches
* Store past calculations in a database so users can see their BMI history over time
* Add input validation feedback directly on the form using JavaScript before submission
