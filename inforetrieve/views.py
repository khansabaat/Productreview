from elasticsearch import Elasticsearch
from rest_framework.response import Response
from rest_framework.views import APIView


class Search(APIView):
    def get(self, request):
        query = {
            "query": {
                "match": {
                    "review/text": request.data["text"]
                }
            },
            "sort": [
                {"review/score": {"order": "desc"}},
                {"review/helpfulness": {"order": "desc"}}
            ],
            "highlight": {
                "fields": {
                    "review/text": {}
                }
            }
        }
        es = Elasticsearch()
        res = es.search(query, "reviews")
        if res["hits"]["total"]["value"]:
            doc = res["hits"]["hits"][0]
            highlighttext = doc["highlight"]["review/text"][0]
            return Response(highlighttext)
        return Response(status=204)

