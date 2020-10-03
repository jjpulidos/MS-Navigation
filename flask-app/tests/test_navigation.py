import pytest
import requests

def test_insert_doc():
    doc = {
        "id": "link/1112",
    }
    response = requests.post("http://127.0.0.1/deleteDoc", data=doc)
    print(response.json())

