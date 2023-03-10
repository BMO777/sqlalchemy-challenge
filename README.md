# sqlalchemy-challenge

In the SunSoak folder will be found a jupyter notebook file named climate and a python file containing code to run a flask app within app.py. 

Also there will be a resource folder with hawaii.sqlite database file from which data will be extracted from for use in designing queries, outputting graphs, and creating a flask app to reference the data within the sqlite database. 

The code in the Jupyter notebook finds temperature measuring station data, most notably the date and temperature.

The app.py file contains code for a flask app that queries stations, temperature and percipitation data observed one year before the latest tempertature measurement, lastly it allows for queries using the browser search for dates within the database and returns 404 if the queries are out of bounds or are nonconforming in some way.

To run:
Requires python3 with the librarires: flask, sqlalchemy and pandas. Applications recommended: Jupyters notebook for the notebook and Visual Studio Code for the python app file.
