"""
firestore_service.py

All of the code that talks to the cloud database (Google Firebase Firestore)
lives in this one file. Keeping it separate from views.py means the views only
say WHAT they want ("save this record", "give me the history") and this file
knows HOW to do it with Firestore.

FIRESTORE IN ONE PARAGRAPH:
    Firestore is a NoSQL cloud database. Instead of tables and rows it stores
    DOCUMENTS (like Python dictionaries) inside COLLECTIONS (like folders of
    documents). Here we use one collection called "bmi_records" and every
    saved calculation is one document in it. Firestore gives each document a
    unique ID automatically.

HOW WE TALK TO IT:
    Firestore has a REST API: ordinary HTTPS requests to
    https://firestore.googleapis.com. We call it with the "requests" library:
        POST   -> create a document          (save_record)
        POST   -> run a query                (get_history)
        PATCH  -> change fields of a document (update_note)
        DELETE -> remove a document          (delete_record)
    Every request carries the project's web API key (?key=...). That key is
    not a password -- Firebase web keys are designed to be public -- access is
    controlled by the Firestore Security Rules set in the Firebase console.

    Firestore REST wraps every value in a type label, for example
    {"doubleValue": 22.5} or {"stringValue": "Obese"}, so small helper
    functions below convert between normal Python values and that format.

The project ID and API key can be overridden with the environment variables
FIREBASE_PROJECT_ID and FIREBASE_API_KEY.
"""

import os
from datetime import datetime, timezone

import requests

# --- Firebase project settings (from the Firebase console "web app" config) ---
PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "bmi-b65df")
API_KEY = os.environ.get("FIREBASE_API_KEY", "AIzaSyB_0_V_jUTUh81DwTfeSyh0mG3khsAIS2g")

# The name of the Firestore collection that holds every saved calculation.
COLLECTION_NAME = "bmi_records"

# Base address of the project's database documents.
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

# How long to wait for Firestore before giving up (seconds), so a network
# problem cannot freeze the web page.
TIMEOUT = 10

# Holds a short description of the most recent failure so the History page can
# show the real reason (for example "permission denied") instead of a blank.
last_error = ""


def get_db():
    """
    Check that the Firebase settings are present.

    Returns:
        The base URL string if the project ID and API key are set, otherwise
        None. The views only use this to decide whether to show the
        "not connected" message.
    """
    if PROJECT_ID and API_KEY:
        return BASE_URL
    return None


def _to_fields(data):
    """
    Convert a normal Python dictionary into Firestore's typed format.

    Example: {"bmi": 22.5, "category": "Normal weight"} becomes
             {"bmi": {"doubleValue": 22.5}, "category": {"stringValue": "Normal weight"}}

    Parameters:
        data -- dictionary of str, int/float or datetime values

    Returns:
        A dictionary Firestore's REST API understands.
    """
    fields = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            # Timestamps are sent as ISO 8601 text ending in "Z" (UTC).
            fields[key] = {"timestampValue": value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
        elif isinstance(value, (int, float)):
            fields[key] = {"doubleValue": float(value)}
        else:
            fields[key] = {"stringValue": str(value)}
    return fields


def _from_fields(fields):
    """
    Convert Firestore's typed format back into a normal Python dictionary.

    Parameters:
        fields -- the "fields" dictionary from a Firestore document

    Returns:
        A plain dictionary, with timestamps turned into datetime objects so
        Django templates can format them with the |date filter.
    """
    result = {}
    for key, typed in fields.items():
        if "doubleValue" in typed:
            result[key] = typed["doubleValue"]
        elif "integerValue" in typed:
            result[key] = int(typed["integerValue"])
        elif "timestampValue" in typed:
            text = typed["timestampValue"].rstrip("Z")
            # Firestore may return up to 9 decimal places; Python allows 6.
            if "." in text:
                whole, fraction = text.split(".")
                text = f"{whole}.{fraction[:6]}"
            result[key] = datetime.fromisoformat(text).replace(tzinfo=timezone.utc)
        else:
            result[key] = typed.get("stringValue", "")
    return result


def _check(response):
    """
    Raise a readable error if Firestore replied with a failure status.

    Parameters:
        response -- the requests.Response object from Firestore

    Returns:
        Nothing. It raises RuntimeError with Firestore's own message if the
        status code is 400 or higher (e.g. 403 = security rules refused it).
    """
    if response.status_code >= 400:
        try:
            message = response.json().get("error", {}).get("message", response.text)
        except ValueError:
            message = response.text
        raise RuntimeError(f"Firestore error {response.status_code}: {message}")


def save_record(height_cm, weight_kg, bmi, category):
    """
    CREATE: add one BMI calculation to the cloud database.

    Parameters:
        height_cm -- height the user typed, in centimeters
        weight_kg -- weight the user typed, in kilograms
        bmi       -- the calculated BMI (already rounded)
        category  -- the category text, e.g. "Normal weight"

    Returns:
        The new document's ID (a string) if it was saved, otherwise None.
    """
    global last_error
    if get_db() is None:
        return None
    try:
        body = {"fields": _to_fields({
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "bmi": bmi,
            "category": category,
            "note": "",
            "created_at": datetime.now(timezone.utc),
        })}
        # POST to the collection address makes Firestore create a new document
        # with an automatically generated ID.
        response = requests.post(
            f"{BASE_URL}/{COLLECTION_NAME}", params={"key": API_KEY},
            json=body, timeout=TIMEOUT)
        _check(response)
        last_error = ""
        # The reply's "name" looks like ".../bmi_records/AbC123": the ID is the last part.
        return response.json()["name"].split("/")[-1]
    except Exception as error:
        last_error = str(error)
        print(f"Could not save record: {error}")
        return None


def get_history(limit=20):
    """
    READ: fetch the most recent saved calculations, newest first.

    Parameters:
        limit -- the maximum number of records to return (default 20)

    Returns:
        A list of dictionaries. Each has the document's fields plus an "id"
        key so the page can tell Firestore which record to update or delete.
        Returns an empty list if there is no connection or on any error
        (the reason is stored in last_error).
    """
    global last_error
    if get_db() is None:
        return []
    try:
        # A "structured query" asks Firestore to sort and limit the results.
        query = {"structuredQuery": {
            "from": [{"collectionId": COLLECTION_NAME}],
            "orderBy": [{"field": {"fieldPath": "created_at"}, "direction": "DESCENDING"}],
            "limit": limit,
        }}
        response = requests.post(
            f"{BASE_URL}:runQuery", params={"key": API_KEY},
            json=query, timeout=TIMEOUT)
        _check(response)
        last_error = ""

        records = []
        for item in response.json():
            # When the collection is empty Firestore returns one item with no
            # "document" in it, so skip anything without one.
            document = item.get("document")
            if document:
                data = _from_fields(document.get("fields", {}))
                data["id"] = document["name"].split("/")[-1]
                records.append(data)
        return records
    except Exception as error:
        last_error = str(error)
        print(f"Could not read history: {error}")
        return []


def update_note(record_id, note):
    """
    UPDATE: change the "note" field of one saved record.

    Parameters:
        record_id -- the Firestore document ID of the record to change
        note      -- the new note text (trimmed and limited to 200 characters)

    Returns:
        True if the update worked, False otherwise.
    """
    global last_error
    if get_db() is None:
        return False
    try:
        # updateMask.fieldPaths tells Firestore to change ONLY the "note"
        # field and leave the other fields alone.
        response = requests.patch(
            f"{BASE_URL}/{COLLECTION_NAME}/{record_id}",
            params={"key": API_KEY, "updateMask.fieldPaths": "note"},
            json={"fields": _to_fields({"note": note.strip()[:200]})},
            timeout=TIMEOUT)
        _check(response)
        last_error = ""
        return True
    except Exception as error:
        last_error = str(error)
        print(f"Could not update record: {error}")
        return False


def delete_record(record_id):
    """
    DELETE: permanently remove one saved record.

    Parameters:
        record_id -- the Firestore document ID of the record to remove

    Returns:
        True if the delete worked, False otherwise.
    """
    global last_error
    if get_db() is None:
        return False
    try:
        response = requests.delete(
            f"{BASE_URL}/{COLLECTION_NAME}/{record_id}",
            params={"key": API_KEY}, timeout=TIMEOUT)
        _check(response)
        last_error = ""
        return True
    except Exception as error:
        last_error = str(error)
        print(f"Could not delete record: {error}")
        return False
