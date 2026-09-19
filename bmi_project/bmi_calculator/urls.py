"""
urls.py (app-level)

Maps URL paths to the view functions in views.py for the bmi_calculator app.

WHY THERE ARE TWO urls.py FILES:
    - bmi_project/urls.py  is the PROJECT-level file. It is the first place
      Django looks, and it hands everything off to this app using include().
    - bmi_calculator/urls.py (this file) is the APP-level file. It decides which
      view function handles each page of the app.
    Splitting them keeps the app self-contained and reusable.

HOW A URL IS MATCHED:
    Django compares the requested path against the entries below from top to
    bottom and uses the first one that matches. The leading "/" and the
    "?height=...&weight=..." query string are NOT part of the path being matched.
        http://127.0.0.1:8000/                  -> path ""        -> views.home
        http://127.0.0.1:8000/result/?height=.. -> path "result/" -> views.result
        http://127.0.0.1:8000/tips/?category=.. -> path "tips/"   -> views.tips
"""

# path() creates one URL rule (a pattern plus the view that handles it).
from django.urls import path

# "from . import views" imports views.py from this same folder (the "." means
# "the current package") so we can refer to views.home, views.result, etc.
from . import views

# 'name=' lets templates refer to these URLs by name instead of hard-coding
# paths, using the {% url %} template tag.
# For example, {% url 'result' %} is turned into "/result/" by Django. If the
# path ever changes, only this file needs updating, not every template.
# urlpatterns is the special list name Django looks for -- it must be spelled
# exactly this way.
urlpatterns = [
    # Empty string = the site's root address (the home page).
    path("", views.home, name="home"),
    # The home page's form submits here. Handled by the result() view.
    path("result/", views.result, name="result"),
    # The "See Tips" link on the result page goes here. Handled by tips().
    path("tips/", views.tips, name="tips"),
]
