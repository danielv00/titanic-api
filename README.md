# titanic-api
Repository for web service that exposes data related to Titanic passengers.<br><br>
Contains the follwoing files:<br>
    app.log - log file that reflects tha requests shown in titanic_api.ipynb<br>
              at first with CSV selected as DATA_SOURCE in config.ini file<br>
              then with DATABASE selected as DATA_SOURCE in config.ini file<br>
              last request was sent with invalid DATA_SOURCE to show the errors in such case<br>
    swagger.json - swagger documentation in json format<br>
    titanic.csv - titanic passengers data in csv<br>
    titanic.db - titanic passengers data in sqlite3 db file<br>
    titanic.py - web service implementation<br>
    titanic_api.ipynb - usages of the web service<br>
    config.ini - configuration file where you can set the follwoing attributes:<br>
                  DATA_SOURCE - can be CSV / DATABASE /  not supported source<br>
                  LOG_LEVEL - logging log level<br>
                  CSV_PATH - titanic passengers data csv file <br>
                  DB_PATH - titanic passengers db file <br><br>


Required modules for this repository:<br>
pandas matplotlib numpy configparser aiosqlite aiofiles uvicorn<br><br>

How to run this web service? Execute the follwoing command:<br>
python -m uvicorn titanic:app --reload<br><br>

After running the service on local machine the Swagger documentation can be found here:<br>
http://localhost:8000/docs<br>
                
