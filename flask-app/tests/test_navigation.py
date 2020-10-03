import pytest
import requests

def test_insert_doc():
    doc = {
        "id": "link/1112",
    }
    response = requests.post("http://75.101.185.140/deleteDoc", data=doc)
    print(response.json())

