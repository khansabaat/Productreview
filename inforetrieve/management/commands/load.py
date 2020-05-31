from django.conf import settings
from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch(settings.ELASTICSEARCH_URL)


class Command(BaseCommand):
    help = "Loads review data into database"
    keys = [
        "product/productId",
        "review/userId",
        "review/profileName",
        "review/helpfulness",
        "review/score",
        "review/time",
        "review/summary",
        "review/text",
    ]

    def add_arguments(self, parser):
        parser.add_argument("file_name", nargs="?", type=str)
        parser.add_argument(
            "--batch_size", help="No. of reviews to process in one batch", default=500
        )

    def dataiter(self, file_name):
        cnt = 1
        with open(file_name, encoding="latin-1") as f:
            obj = list()
            while True:
                line = f.readline()
                if not line:
                    return
                if line == "\n":
                    doc = dict(
                        (self.keys[index], ob.lstrip(f"{self.keys[index]}: "))
                        for index, ob in enumerate(obj)
                    )
                    try:
                        doc["review/helpfulness"] = eval(doc["review/helpfulness"])
                    except ZeroDivisionError:
                        doc["review/helpfulness"] = 0

                    doc = {
                        "_op_type": "update",
                        "doc_as_upsert": True,
                        "_index": "reviews",
                        "_id": cnt,
                        "doc": doc,
                    }
                    obj = list()
                    cnt += 1
                    self.stdout.write(self.style.NOTICE(f"Processing {cnt}th record"))
                    yield doc
                elif line.startswith("product/") or line.startswith("review/"):
                    obj.append(line.rstrip())
                else:
                    obj[-1] += line.strip()

    def loaddata(self, file_name, batch_size):
        helpers.bulk(es, self.dataiter(file_name), chunk_size=batch_size)

    def update_mapping(self):
        mapping = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "my_analyzer": {
                            "tokenizer": "keyword",
                            "char_filter": ["my_char_filter"],
                        }
                    },
                    "char_filter": {"my_char_filter": {"type": "html_strip",}},
                }
            },
            "mappings": {
                "properties": {
                    "review/helpfulness": {"type": "float"},
                    "review/score": {"type": "float"},
                }
            },
        }
        es.indices.create("reviews", mapping, ignore=400)

    def handle(self, *args, **options):
        file_name = options["file_name"]
        batch_size = options["batch_size"]
        self.update_mapping()
        self.stdout.write(self.style.SUCCESS("Mapping updated"))

        self.loaddata(file_name, batch_size)

        self.stdout.write(self.style.SUCCESS("Successfully loaded data"))
