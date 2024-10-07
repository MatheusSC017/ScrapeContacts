from flask import Flask, request
from flask_restful import Api, Resource
from src.etl import etl_contacts
import asyncio
import json


def create_app():
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(ETLContacts, "/")
    return app


class ETLContacts(Resource):
    def post(self):
        parameters = json.loads(request.get_json())
        if 'search_term' not in parameters.keys():
            return {}

        contacts = asyncio.run(etl_contacts(parameters['search_term'],
                                            parameters.get('output', 'contacts.csv'),
                                            parameters.get('number', 10),
                                            parameters.get('exclude', [])))

        return {contact[0]: contact[1:] for contact in contacts}
