from datetime import datetime
from bs4 import BeautifulSoup
import requests
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    class_id: str
    tags: str
    type: str


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
    tags = {}
    for hit in res['hits']['hits']:
        hit = hit.get("_source")
        if hit.get("tags") not in tags.keys():
            tags[hit.get("tags")] = [hit]
        else:
            tags[hit.get("tags")].append(hit)
    return tags


@app.get("/listDocs/type")
def list_doc_type():
    res = es.search(index="dev_westudy", body={"query": {"match_all": {}}})
    type = {}
    for hit in res['hits']['hits']:
        hit = hit.get("_source")
        if hit.get("type") not in type.keys():
            type[hit.get("type")] = [hit]
        else:
            type[hit.get("type")].append(hit)
    return type


@app.post("/searchDocs/text")
def search_doc_text(text: str):
    res = es.search(index="dev_westudy", body={
        "query": {
            "match": {
                "text": text
            }
        }
    })

    response = {"data": [data.get("_source") for data in res['hits']['hits']]}
    return response


@app.post("/searchDocs/tags")
def search_doc_tags(tags: str):
    res = es.search(index="dev_westudy", body={
        "query": {
            "match": {
                "tags": tags
            }
        }
    })
    response = {"data": [data.get("_source") for data in res['hits']['hits']]}
    return response


@app.post("/searchDocs/type")
def search_doc_type(type: str):
    res = es.search(index="dev_westudy", body={
        "query": {
            "match": {
                "type": type
            }
        }
    })
    response = {"data": [data.get("_source") for data in res['hits']['hits']]}
    return response


@app.delete("/deleteDoc")
def delete_doc(id: str):
    res = es.delete(index="dev_westudy", id=id)
    return res['result']
