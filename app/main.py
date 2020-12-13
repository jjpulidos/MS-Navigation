from datetime import datetime
from bs4 import BeautifulSoup
import requests
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from elasticsearch import Elasticsearch

app = FastAPI()
es = Elasticsearch("https://search-we-study-nckckstkdcnxiwgokq4vteczgq.us-east-1.es.amazonaws.com")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

blacklist = [
    '[document]',
    'noscript',
    'header',
    'html',
    'meta',
    'head',
    'input',
    'script',
    # there may be more elements you don't want, such as "style", etc.
]


class Item(BaseModel):
    class_id: Optional[str] = None
    tags: Optional[str] = None
    type: Optional[str] = None
    text: Optional[str] = None


def item2doc(item: Item):
    text_output = ""
    res = requests.get(item.class_id)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text=True)
    for t in text:
        if t.parent.name not in blacklist:
            text_output += '{} '.format(t)

    return {
        "class": item.class_id,
        "tags": item.tags,
        "type": item.type,
        "text": text_output
    }


@app.get("/health")
def health():
    return es.info()


@app.put("/insertDoc")
def insert_doc(item: Item):
    res = es.index(index="dev_westudy", id=item.class_id, body=item2doc(item))
    return res['result']


@app.get("/listDocs")
def list_docs():
    res = es.search(index="dev_westudy", body={"query": {"match_all": {}}})
    response = {"data": [data.get("_source") for data in res['hits']['hits']]}
    return response


@app.get("/listDocs/tags")
def list_doc_tags():
    res = es.search(index="dev_westudy", body={"query": {"match_all": {}}})
    response = {
        "data": []
    }
    for hit in res['hits']['hits']:
        hit = hit.get("_source")
        if hit.get("tags") not in [elem.get("name") for elem in response.get("data")]:
            response.get("data").append({
                "name": hit.get("tags"),
                "docs": [hit]
            })
        else:
            response.get("data")[[elem.get("name") for elem in response.get("data")].index(hit.get("tags"))].get("docs").append(hit)
    return response


@app.get("/listDocs/type")
def list_doc_type():
    res = es.search(index="dev_westudy", body={"query": {"match_all": {}}})
    response = {
        "data": []
    }
    for hit in res['hits']['hits']:
        hit = hit.get("_source")
        if hit.get("type") not in [elem.get("name") for elem in response.get("data")]:
            response.get("data").append({
                "name": hit.get("type"),
                "docs": [hit]
            })
        else:
            response.get("data")[[elem.get("name") for elem in response.get("data")].index(hit.get("type"))].get(
                "docs").append(hit)
    return response


@app.post("/searchDocs/text")
def search_doc_text(item: Item):
    res = es.search(index="dev_westudy", body={
        "query": {
            "match": {
                "text": item.text
            }
        }
    })

    response = {"data": [data.get("_source") for data in res['hits']['hits']]}
    return response


@app.post("/searchDocs/tags")
def search_doc_tags(item: Item):
    res = es.search(index="dev_westudy", body={
        "query": {
            "match": {
                "tags": item.tags
            }
        }
    })
    response = {"data": [data.get("_source") for data in res['hits']['hits']]}
    return response


@app.post("/searchDocs/type")
def search_doc_type(item: Item):
    res = es.search(index="dev_westudy", body={
        "query": {
            "match": {
                "type": item.type
            }
        }
    })
    response = {"data": [data.get("_source") for data in res['hits']['hits']]}
    return response


@app.post("/deleteDoc")
def delete_doc(item: Item):
    query = {
        "query": {
            "match": {
                "class": item.class_id
            }
        }
    }

    res = es.search(index="dev_westudy", body=query)
    print(res)
    res = es.delete_by_query(index="dev_westudy", body=query)

    return res


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)