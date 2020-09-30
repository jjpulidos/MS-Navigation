from datetime import datetime
from flask import Flask, render_template, url_for, redirect, request
from flask_restplus import Api, Resource, fields
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch("https://search-we-study-nckckstkdcnxiwgokq4vteczgq.us-east-1.es.amazonaws.com")

@app.route("/insertDoc", methods=['PUT'])
def insert_doc():
    data = request.json
    res = es.index(index="dev_westudy", id=data.get("class"), body=data)
    return res['result']


@app.route("/listDocs", methods=['GET'])
def list_docs():
    res = es.search(index="dev_westudy", body={"query": {"match_all": {}}})
    response = {"data": [data.get("_source") for data in res['hits']['hits']]}
    return response


@app.route("/listDocs/tags", methods=['GET'])
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


@app.route("/listDocs/type")
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


@app.route("/searchDocs/text", methods=["POST"])
def search_doc_text():
    data = request.json
    res = es.search(index="dev_westudy", body={
        "query": {
            "match": {
                "text": data.get("text")
            }
        }
    })
    response = {"data": [data.get("_source") for data in res['hits']['hits']]}
    return response


@app.route("/searchDocs/tags", methods=["POST"])
def search_doc_tags():
    data = request.json
    res = es.search(index="dev_westudy", body={
        "query": {
            "match": {
                "tags": data.get("tags")
            }
        }
    })
    response = {"data": [data.get("_source") for data in res['hits']['hits']]}
    return response


@app.route("/searchDocs/type", methods=["POST"])
def search_doc_type():
    data = request.json
    res = es.search(index="dev_westudy", body={
        "query": {
            "match": {
                "type": data.get("type")
            }
        }
    })
    response = {"data": [data.get("_source") for data in res['hits']['hits']]}
    return response


@app.route("/health")
def health():
    if es:
        return "ES esta vivo"

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8001, debug=True)


# res = es.get(index="dev_westudy")
# print(res['_source'])

# es.indices.refresh(index="test-index")
#