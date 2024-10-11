# Scrape Contacts

This project aims to be a simple ETL that searches websites using a specific term and collects contact information such as email and phone number. Its functionality was designed to be a tool to easily identify potential customers/leads and extract their contact information for future use.

## Usage

Use the command below to run the API in the port 5000

> flask --app src run

## Docker

Run the commands below to build and run the container image

> docker build -t scrap_contacts .

> docker run scrap_contacts

## Endpoints:

### /
This endpoint accepts POST and GET methods, you can use these methods to request a contact search based on a specific term and retrieve the last storage search for those terms respectively.

#### POST json parameters

- search_term: Required parameter, represent the term used during the search.
- number: Optional parameter, that delimit the number of results, the pattern value is 10.
- exclude: Optional parameter, you can set to exclude specific links from the search.

#### GET json parameters

- cached_search: Optional parameter, represent the term used during the search and the name used to save tha cached results. If this parameter is not provided, the endpoint will return a list of all cached results.