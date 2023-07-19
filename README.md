# titanic-api
Repository for web service that exposes data related to Titanic passengers.
Contains the follwoing files:
    app.log - log file that reflects tha requests shown in titanix_api.ipynb
              at first with CSV selected as DATA_SOURCE in config.ini file
              then with DATABASE selected as DATA_SOURCE in config.ini file
              last request was sent with invalid DATA_SOURCE to show the errors in such case
    swagger.json - swagger documentation in json format
    titanic.csv - titanic passengers data in csv
    titanic.db - titanic passengers data in sqlite3 db file
    titanic.py - web service implementation
    titanic_api.ipynb - usages of the web service
    config.ini - configuration file where you can set the follwoing attributes:
                  DATA_SOURCE - can be CSV / DATABASE /  not supported source
                  LOG_LEVEL - logging log level
                  CSV_PATH - titanic passengers data csv file 
                  DB_PATH - titanic passengers db file 


Required modules for this repository:
pandas matplotlib numpy configparser aiosqlite aiofiles uvicorn

How to run this web service? Execute the follwoing command:
python -m uvicorn titanic:app --reload

After running the service on local machine the Swagger documentation can be found here:
http://localhost:8000/docs
                
