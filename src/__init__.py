from flask import Flask, request
from flask_restful import Api, Resource
from src.etl import etl_contacts, read_cache
import asyncio
import json
import unicodedata
import re
import os


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
            cached_searches = [search_file[:-4] for search_file in os.listdir('cache')]
            return {'cached_searches': cached_searches}

        if 'cached_search' not in parameters.keys():
            return {}

        nfkd_str = unicodedata.normalize('NFKD', parameters['cached_search'])
        no_accents = ''.join([c for c in nfkd_str if not unicodedata.combining(c)])
        cached_search_filename = re.sub(r'\s+', '_', no_accents).lower()
        contacts = read_cache(cached_search_filename)
        return {contact[0]: contact[1:] for contact in contacts}

    def post(self):
        parameters = json.loads(request.get_json())
        if 'search_term' not in parameters.keys():
            return {}

        nfkd_str = unicodedata.normalize('NFKD', parameters['search_term'])
        no_accents = ''.join([c for c in nfkd_str if not unicodedata.combining(c)])
        output_filename = re.sub(r'\s+', '_', no_accents).lower()

        contacts = asyncio.run(etl_contacts(parameters['search_term'],
                                            f'{output_filename}.csv',
                                            parameters.get('number', 10),
                                            parameters.get('exclude', [])))

        return {contact[0]: contact[1:] for contact in contacts}
