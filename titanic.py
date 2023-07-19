from fastapi import FastAPI, Query
from typing import Optional, List
from starlette.responses import JSONResponse
from starlette.requests import Request
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import logging
import configparser
import sqlite3
from sqlite3 import Error
import asyncio
import datetime
import aiofiles
import aiosqlite
from io import StringIO
# import uvicorn

#TODO: add documentation to methods to show in swager

app = FastAPI(title="Titanic API", description="API for Titanic passengers data", version="1.1.0")

# Set config file
config = configparser.ConfigParser()
config.read('config.ini')

# Set up logging
log_level = config.get('LOG', 'LOG_LEVEL')
logging.basicConfig(filename='app.log', level=log_level)

def get_timestamp():
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")


# Function to create a connection to the SQLite database
async def create_db_connection():
    """
    This method creates a connection to the SQLite database.
    It returns the connection object if successful, or None otherwise.
    """
    conn = None
    try:
        db_path = config.get('DATABASE', 'DB_PATH')
        logging.debug(f"Creating connection to {db_path} at {get_timestamp()}")
        conn = await aiosqlite.connect(db_path)
        return conn
    except Exception as ex:
        logging.error(f"Error connecting to database: {ex}")

# Function to load data from the SQLite database
async def load_data_from_db():
    """
    This method loads data from the SQLite database.
    It returns a pandas DataFrame containing the data if successful, or None otherwise.
    """
    conn = None
    try:
        conn = await create_db_connection()
        if conn is None:
            return None
        table_name = 'Passengers' 
        logging.debug(f"Loading data from {table_name} table at {get_timestamp()}")
        async with conn.execute(f"SELECT * from {table_name}") as cursor:
            data = await cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            df = pd.DataFrame(data, columns=column_names)
        return df
    except Exception as ex:
        logging.error(f"Error loading data from database: {ex}")
        return None
    finally:
        if conn:
            await conn.close()

# Function to load data from a CSV file
async def load_data_from_csv():
    """
    This method loads data from a CSV file.
    It returns a pandas DataFrame containing the data if successful, or None otherwise.
    """
    try:
        path = config.get('CSV', 'CSV_PATH')
        logging.debug(f"Loading data from csv: {path} at {get_timestamp()}")
        async with aiofiles.open(path, mode='r') as f:
            data = await f.read()
        df = pd.read_csv(StringIO(data))
        return df
    except Exception as ex:
        logging.error(f"Error loading data from CSV: {ex}")
        return None

    
async def load_data():
    """
    This method loads data based on the data source specified in the configuration file.
    It sets data into DataFrame if successful, or sets None otherwise.
    """
    data_source = config.get('DATA', 'DATA_SOURCE')
    global df
    
    match data_source:
        case 'CSV':
            df = await load_data_from_csv() 
        case 'DATABASE':
            df = await load_data_from_db()
        case _:
            logging.error(f"Error: Uknown data source -  '{data_source}'")
            df = None
    logging.info(f"Loaded total of {len(df) if df is not None else 'None'} passengers")

@app.on_event("startup")
async def on_startup():
    """
    This method is executed when the FastAPI application starts up.
    It loads the data into a global pandas DataFrame.
    """
    logging.info(f"Service was restarted at {get_timestamp()}")
    logging.debug(f"{log_level=}")
    await load_data()

@app.on_event("shutdown")
async def shutdown_event():
    """
    This method is executed when the FastAPI application is shutting down.
    It logs a message indicating that the service is shutting down.
    """
    logging.info(f"Shutting down service at {get_timestamp()}")
    
@app.get("/")
async def read_root():
    """
    This function handles GET requests to the root URL ("/").
    It returns a welcome message.
    """
    return "Welcome to Titanic API!"


@app.get('/fare_histogram')
async def fare_histogram():
    """
    This function handles GET requests to the "/fare_histogram" URL.
    It calculates and returns a histogram data of passenger fares.
    Rendering the response on server side is not optimal due to traffic overhead,
    therefore the rendering can be done on client side and the response body will contain only the numerical histogram data.
    """
    try:
        # If no data - try to load data one more time
        if df is None:
            await load_data()
        # If still no data - do not proceed
        if df is None:
            logging.error(f"Unable to proceed with the request due to data source issue")
            return JSONResponse(content = 'data source issue', status_code=500)
        
        logging.info(f"Executing GET for fare_histogram at {get_timestamp()}")
        # Calculate the percentiles
        percentiles = np.percentile(df['Fare'], np.arange(0, 100, 10))

        # Calculate the histogram
        hist, bin_edges = np.histogram(df['Fare'], bins=percentiles)

        # Prepare the data for JSON
        data = {
            'percentiles': percentiles.tolist(),
            'counts': hist.tolist(),
        }

        return data

    except Exception as ex:
        logging.error(f"Error creating fare histogram: {ex}")
        return JSONResponse(status_code=500)
    
@app.get('/passenger/{passenger_id}')
async def passenger(passenger_id: int, attributes: Optional[str] = Query(None)):
    """
    This function handles GET requests to the "/passenger/{passenger_id}" URL.
    It returns the data for the passenger with the given ID.
    If the "attributes" query parameter is provided, only the specified attributes are returned.
    """
    try:
        logging.info(f"Executing GET for passenger_id = {passenger_id} at {get_timestamp()}")
        
        # If no data - try to load data one more time
        if df is None:
            await load_data()
        # If still no data - do not proceed
        if df is None:
            logging.error(f"Unable to proceed with the request due to data source issue")
            return JSONResponse(content = 'data source issue', status_code=500)
        
        if attributes:
            attributes = attributes.split(',')
            valid_attributes = []
            # Validate the attributes
            for attribute in attributes:
                if attribute in df.columns:
                    valid_attributes.append(attribute)
                else:
                    logging.warning(f"Invalid passenger attribute: {attribute}")
                
        # Find the passenger with the given ID
        passenger = df[df['PassengerId'] == passenger_id]
        if passenger.empty:
            logging.warning(f"Passenger not found for {passenger_id=}")
            return JSONResponse(content=f'Passenger not found for {passenger_id=}',status_code=404)
        logging.debug(f"Found passenger for: {passenger_id=}")
        # Return as JSON
        if attributes:
            return JSONResponse(content=json.loads(passenger[valid_attributes].to_json(orient='records')))
        else:
            return JSONResponse(content=json.loads(passenger.to_json(orient='records')))
    
    except Exception as ex:
        logging.error(f"Error getting passenger id = {passenger_id} error: {ex}")
        return JSONResponse(content={"error": f"{ex}"}, status_code=500)
    
    
@app.get('/passengers')
async def passengers():
    """
    This function handles GET requests to the "/passengers" URL.
    It returns the data for all passengers.
    """
    try:
        logging.info(f"Executing GET for all passengers at {get_timestamp()}")
        
        # If no data - try to load data one more time
        if df is None:
            await load_data()
        # If still no data - do not proceed
        if df is None:
            logging.error(f"Unable to proceed with the request due to data source issue")
            return JSONResponse(content = 'data source issue', status_code=500)

        # Return all passengers as JSON
        return JSONResponse(content=json.loads(df.to_json(orient='records')))
    except Exception as ex:
        logging.error(f"Error getting all passengers: {ex}")
        return JSONResponse(status_code=500)
