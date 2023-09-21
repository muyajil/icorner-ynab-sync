from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from icorner_ynab_sync.ynab_client import YNABClient
import os


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def get_available_amount():
    category_ids = set(os.environ["CATEGORY_IDS"].split(","))
    categories = YNABClient().get_categories()
    values = []
    for category in categories:
        if category["id"] in category_ids:
            available = category["balance"] / 1000
            values.append((category["name"], "{:,.0f}".format(available)))

    color = "#79AC78"

    html = f"""
    <html>
    <head>
        <style>
            body {{
                background-color: {color};
                text-align: center;
                font-family: Arial, sans-serif;
                font-size: 500%;
                color: white;
                padding: 50px;
            }}
        </style>
    </head>
    <body>
    """
    for name, value in values:
        html += f"<div>{name}:<br>{value}</div>"

    return (
        html
        + """
    </body>
    </html>
    """
    )
