"""
Method and script to run the complete ETL, through a call or command line
"""

import argparse
import asyncio

from src.etl import etl_contacts

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ScrapContacts",
        description="Scrap contacts info from page of a specific category",
    )
    parser.add_argument(
        "search_term", type=str, help="Term used during the search for the links"
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Output CSV file name", default="contacts.csv"
    )
    parser.add_argument(
        "-n", "--number", type=int, help="Number of results expected", default=10
    )
    parser.add_argument(
        "-e",
        "--exclude",
        metavar="S",
        type=str,
        nargs="+",
        help="List of sites to exclude from search",
        default=[],
    )

    args = parser.parse_args()

    asyncio.run(etl_contacts(args.search_term, args.output, args.number, args.exclude))
