from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from icorner_ynab_sync.ynab_client import YNABClient
import os


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def get_available_amount():
    category_id = os.environ["AVAILABLE_CATEGORY_ID"]
    available = YNABClient().get_available_amount(category_id)
    if available > 500:
        color = '#79AC78'
    else:
        color = '#EF9595'

    formatted = '{:,.0f}'.format(available)

    return f'''
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
        Available for Wants:<br>CHF {formatted}
    </body>
    </html>
    '''
