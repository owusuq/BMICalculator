"""
views.py

This file contains the "view" functions for the BMI Calculator app.

HOW A DJANGO VIEW WORKS (the big picture):
    1. The user's browser asks for a URL, for example /result/?height=170&weight=65
    2. Django looks that URL up in urls.py and finds which view function to call.
    3. Django calls that function and passes it an "HttpRequest" object. The
       request object holds everything the browser sent us (the URL, the form
       data in request.GET, the HTTP method, etc.).
    4. The view function does its work (read input, calculate, decide what to show).
    5. The view calls render(), which fills an HTML template with our data and
       returns an "HttpResponse". Django sends that HTML back to the browser.

There are three views in this app (one per web page):
    1. home   -> shows the input form (height and weight)
    2. result -> calculates the BMI and shows the number + category
    3. tips   -> shows advice based on the BMI category from the result page

There are also two plain helper functions (calculate_bmi and get_bmi_category).
They are NOT views: they never receive a request and never return a response.
They only do the math / decision-making, which keeps that logic separate from
the web-handling code and makes it easy to test on its own.
"""

# render() is Django's shortcut for: load a template file, fill it in with
# our data (the "context"), and return the finished HTML as an HttpResponse.
from django.shortcuts import render


def calculate_bmi(weight_kg, height_m):
    """
    Calculate BMI given weight in kilograms and height in meters.

    The BMI formula is: weight (kg) / height (m) squared.
    Example: 65 kg and 1.70 m  ->  65 / (1.70 * 1.70)  =  65 / 2.89  =  22.49

    This is a plain helper function (not a view) so it can be
    tested and reused independently of any web request.

    Parameters:
        weight_kg -- the person's weight in kilograms (a number)
        height_m  -- the person's height in METERS (not centimeters)

    Returns:
        The BMI as a float, or 0 if the height is not a valid positive number.
    """
    if height_m <= 0:
        # Guard against division by zero or a negative height.
        # Dividing by 0 would crash the program with a ZeroDivisionError, and a
        # negative height makes no sense, so we return 0 as a safe "no result".
        # (The result view also checks this first, so this is a second safety net.)
        return 0

    # ** is Python's "to the power of" operator, so height_m ** 2 means
    # height squared. The result is a float (a number with decimals).
    return weight_kg / (height_m ** 2)


def get_bmi_category(bmi):
    """
    Convert a numeric BMI value into a human-readable category.
    These thresholds follow the standard World Health Organization
    BMI classification for adults.

    Parameters:
        bmi -- the BMI number produced by calculate_bmi()

    Returns:
        One of four strings: "Underweight", "Normal weight", "Overweight", "Obese".
        Those exact strings are reused as the keys in the tips dictionary in the
        tips() view, so the spelling here must match the spelling there.
    """
    # The checks run from the top down and stop at the FIRST one that is True.
    # That is why each branch only needs an upper limit: by the time we reach
    # "elif bmi < 25", we already know bmi is NOT below 18.5.
    if bmi < 18.5:
        return "Underweight"       # anything below 18.5
    elif bmi < 25:
        return "Normal weight"     # 18.5 up to (but not including) 25
    elif bmi < 30:
        return "Overweight"        # 25 up to (but not including) 30
    else:
        return "Obese"             # 30 and above


def home(request):
    """
    Page 1: Home page.

    Displays a simple HTML form where the user enters their height
    (in centimeters) and weight (in kilograms). This page does not
    do any calculation itself -- it just collects the input and
    submits it (via a GET request) to the 'result' view.

    Parameters:
        request -- the HttpRequest object Django gives every view. We do not
                   need anything from it here, but Django always passes it in.

    Returns:
        The rendered home.html page.
    """
    # No context dictionary is needed because home.html is static: it has no
    # {{ variables }} to fill in. render() just needs the request and the
    # template's path (relative to the app's "templates" folder).
    return render(request, "bmi_calculator/home.html")


def result(request):
    """
    Page 2: Result page.

    Reads the 'height' and 'weight' values submitted from the home
    page's form (sent as GET query parameters), converts them to the
    correct units, calculates the BMI, and figures out which category
    the user falls into. The page is dynamically generated because
    the numbers and category text change based on what the user typed.

    Example of the URL this view receives after the form is submitted:
        /result/?height=170&weight=65
    Everything after the "?" is the "query string". Django parses it into the
    dictionary-like object request.GET, so request.GET["height"] is "170".

    Parameters:
        request -- the HttpRequest; request.GET holds the submitted form values.

    Returns:
        The rendered result.html page, showing either the BMI + category or an
        error message.
    """
    # Pull the raw string values out of the query string. We provide
    # default values in case something is missing so the page does not crash.
    # IMPORTANT: everything in request.GET is a STRING (text), even numbers.
    # .get("height", "") returns "" if the key is missing, instead of raising
    # a KeyError like request.GET["height"] would.
    # The keys "height" and "weight" must match the name="" attributes of the
    # <input> fields in home.html -- that is how the form data reaches this code.
    height_cm = request.GET.get("height", "")
    weight_kg = request.GET.get("weight", "")

    # Start with "nothing to show" for all three results. The template checks
    # these values to decide what to display. If an error happens, they simply
    # stay as None.
    error_message = None
    bmi = None
    category = None

    # try/except lets us attempt risky code and handle failure gracefully
    # instead of letting the whole page crash with a server error.
    try:
        # float() converts the text into a number. This is the risky line:
        # if the text is empty ("") or not numeric ("abc"), Python raises
        # a ValueError, which jumps straight to the except block below.
        height_cm = float(height_cm)
        weight_kg = float(weight_kg)

        # Validation: the text WAS a number, but it must also make sense.
        # Zero or negative height/weight is not possible for a real person, and
        # a height of zero would cause a division-by-zero in the BMI formula.
        if height_cm <= 0 or weight_kg <= 0:
            error_message = "Height and weight must both be positive numbers."
        else:
            # Convert centimeters to meters before calculating BMI.
            # The BMI formula needs meters, but the form asks for centimeters
            # because that is easier for users to type (170 instead of 1.7).
            height_m = height_cm / 100

            # Step 1: calculate the raw BMI with our helper function.
            # round(number, 1) keeps one decimal place, so 22.491349 becomes 22.5
            # and the page shows a clean value.
            bmi = round(calculate_bmi(weight_kg, height_m), 1)

            # Step 2: turn that number into a category word using our other helper.
            category = get_bmi_category(bmi)

    except ValueError:
        # This happens if the user leaves the fields blank or types
        # something that is not a number.
        # (The <input type="number"> in home.html blocks most of this in the
        # browser, but someone can still type a URL by hand, so the server must
        # never trust the input and has to check it itself.)
        error_message = "Please enter valid numbers for height and weight."

    # Everything in this dictionary is passed into the template so it
    # can be displayed dynamically on the page.
    # The dictionary KEYS become the variable names available in result.html:
    # "bmi" -> {{ bmi }}, "category" -> {{ category }}, and so on.
    context = {
        "bmi": bmi,
        "category": category,
        "error_message": error_message,
    }

    # Fill result.html with the context and send the HTML back to the browser.
    return render(request, "bmi_calculator/result.html", context)


def tips(request):
    """
    Page 3: Tips page.

    Takes the BMI category (passed in the query string from the result
    page) and shows a short, dynamically chosen set of health tips that
    match that category. This satisfies the "third dynamically generated
    page" bonus requirement for the Web App module.

    How the category gets here: on the result page, the "See Tips" link is
    written as  /tips/?category=Normal weight  so the category travels in the
    URL's query string, and this view reads it back out with request.GET.

    Parameters:
        request -- the HttpRequest; request.GET holds the "category" value.

    Returns:
        The rendered tips.html page with a list of tips for that category.
    """
    # Read the category from the URL. If it is missing we get "" (empty text).
    category = request.GET.get("category", "")

    # A simple lookup table of tips for each possible category.
    # This is a dictionary: each KEY is a category name (the same strings that
    # get_bmi_category() returns) and each VALUE is a list of tip strings.
    # Using a dictionary means we do not need a long chain of if/elif checks --
    # we just look up the category directly.
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
    # dict.get(key, default) returns the value for that key, or the default if
    # the key does not exist. Someone could type /tips/?category=banana by hand,
    # and without this fallback that would raise a KeyError and crash the page.
    tip_list = tips_by_category.get(category, [])

    # Pass the category (for the page heading) and the tips (for the bullet list)
    # to the template. tips.html loops over tip_list with a {% for %} tag.
    context = {
        "category": category,
        "tip_list": tip_list,
    }
    return render(request, "bmi_calculator/tips.html", context)
