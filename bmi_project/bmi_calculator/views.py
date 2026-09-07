"""
views.py

This file contains the "view" functions for the BMI Calculator app.
In Django, a view function receives an HTTP request, does some work,
and returns an HTTP response (usually rendered from an HTML template).

There are three views in this app:
    1. home   -> shows the input form (height and weight)
    2. result -> calculates the BMI and shows the number + category
    3. tips   -> shows advice based on the BMI category from the result page
"""

from django.shortcuts import render


def calculate_bmi(weight_kg, height_m):
    """
    Calculate BMI given weight in kilograms and height in meters.

    The BMI formula is: weight (kg) / height (m) squared.
    This is a plain helper function (not a view) so it can be
    tested and reused independently of any web request.
    """
    if height_m <= 0:
        # Guard against division by zero or a negative height.
        return 0
    return weight_kg / (height_m ** 2)


def get_bmi_category(bmi):
    """
    Convert a numeric BMI value into a human-readable category.
    These thresholds follow the standard World Health Organization
    BMI classification for adults.
    """
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def home(request):
    """
    Page 1: Home page.

    Displays a simple HTML form where the user enters their height
    (in centimeters) and weight (in kilograms). This page does not
    do any calculation itself -- it just collects the input and
    submits it (via a GET request) to the 'result' view.
    """
    return render(request, "bmi_calculator/home.html")


def result(request):
    """
    Page 2: Result page.

    Reads the 'height' and 'weight' values submitted from the home
    page's form (sent as GET query parameters), converts them to the
    correct units, calculates the BMI, and figures out which category
    the user falls into. The page is dynamically generated because
    the numbers and category text change based on what the user typed.
    """
    # Pull the raw string values out of the query string. We provide
    # default values in case something is missing so the page does not crash.
    height_cm = request.GET.get("height", "")
    weight_kg = request.GET.get("weight", "")

    error_message = None
    bmi = None
    category = None

    try:
        height_cm = float(height_cm)
        weight_kg = float(weight_kg)

        if height_cm <= 0 or weight_kg <= 0:
            error_message = "Height and weight must both be positive numbers."
        else:
            # Convert centimeters to meters before calculating BMI.
            height_m = height_cm / 100
            bmi = round(calculate_bmi(weight_kg, height_m), 1)
            category = get_bmi_category(bmi)

    except ValueError:
        # This happens if the user leaves the fields blank or types
        # something that is not a number.
        error_message = "Please enter valid numbers for height and weight."

    # Everything in this dictionary is passed into the template so it
    # can be displayed dynamically on the page.
    context = {
        "bmi": bmi,
        "category": category,
        "error_message": error_message,
    }
    return render(request, "bmi_calculator/result.html", context)


def tips(request):
    """
    Page 3: Tips page.

    Takes the BMI category (passed in the query string from the result
    page) and shows a short, dynamically chosen set of health tips that
    match that category. This satisfies the "third dynamically generated
    page" bonus requirement for the Web App module.
    """
    category = request.GET.get("category", "")

    # A simple lookup table of tips for each possible category.
    tips_by_category = {
        "Underweight": [
            "Consider adding more nutrient-dense meals and snacks to your day.",
            "Strength training can help build healthy muscle mass.",
            "Talk with a healthcare provider if you are struggling to gain weight.",
        ],
        "Normal weight": [
            "Keep up your current balance of activity and nutrition.",
            "Regular exercise helps maintain your healthy weight long-term.",
            "Continue routine checkups to track your health over time.",
        ],
        "Overweight": [
            "Small, consistent changes to diet and activity add up over time.",
            "Aim for regular physical activity most days of the week.",
            "Consider tracking meals to build awareness of eating habits.",
        ],
        "Obese": [
            "Speaking with a healthcare provider can help you build a safe plan.",
            "Focus on small, sustainable changes rather than drastic ones.",
            "Regular movement, even short walks, can make a meaningful difference.",
        ],
    }

    # Fall back to an empty list if an unexpected/missing category is passed in.
    tip_list = tips_by_category.get(category, [])

    context = {
        "category": category,
        "tip_list": tip_list,
    }
    return render(request, "bmi_calculator/tips.html", context)
