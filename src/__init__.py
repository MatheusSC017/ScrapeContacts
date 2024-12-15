"""
Flask API related methods and classes
"""

import asyncio
import json
import re
import unicodedata

from flask import Flask, request
from flask_restful import Api, Resource

from src.etl import etl_contacts, read_cache

cache = {}
cache_limit = 100


def create_app():
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(ETLContacts, "/")
    return app


class ETLContacts(Resource):
    def get(self):
        if request.content_type:
            parameters = json.loads(request.get_json())
        else:
            return {"cached_searches": list(cache.keys())}

        if "cached_search" not in parameters.keys():
            return {}

        nfkd_str = unicodedata.normalize("NFKD", parameters["cached_search"])
        no_accents = "".join([c for c in nfkd_str if not unicodedata.combining(c)])
        cached_search_filename = re.sub(r"\s+", "_", no_accents).lower()

        contacts = cache.get(cached_search_filename, {})
        return {contact[0]: contact[1:] for contact in contacts}

    def post(self):
        parameters = json.loads(request.get_json())
        if "search_term" not in parameters.keys():
            return {}

        nfkd_str = unicodedata.normalize("NFKD", parameters["search_term"])
        no_accents = "".join([c for c in nfkd_str if not unicodedata.combining(c)])
        output_filename = re.sub(r"\s+", "_", no_accents).lower()

        contacts = asyncio.run(
            etl_contacts(
                parameters["search_term"],
                f"{output_filename}.csv",
                parameters.get("number", 10),
                parameters.get("exclude", []),
            )
        )

        if len(cache) == cache_limit:
            del cache[cache.keys()[0]]

        cache[output_filename] = contacts

        return {contact[0]: contact[1:] for contact in contacts}
