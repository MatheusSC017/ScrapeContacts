from flask import Flask, request
from flask_restful import Api, Resource
from src.etl import etl_contacts, read_cache
import asyncio
import json
import unicodedata
import re


def create_app():
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(ETLContacts, "/")
    return app


class ETLContacts(Resource):
    def get(self):
        parameters = json.loads(request.get_json())
        if 'cached_search' not in parameters.keys():
            return {}

        contacts = read_cache(parameters['cached_search'])
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
