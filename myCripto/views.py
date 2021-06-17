from myCripto import app
from flask import render_template, jsonify, request
from myCripto.dataaccess import DBmanager
from http import HTTPStatus
import sqlite3

dbManager = DBmanager(app.config.get('DATABASE'))

@app.route('/')
def listaMovimientos(): 
    return render_template('spa.html')

@app.route('/api/v1/movimientos') # Ruta de las APIs
def movimientosAPI():
    query = "SELECT * FROM movimientos ORDER BY date;"

    try:
        lista = dbManager.consultaMuchasSQL(query)
        return jsonify({'status': 'success', 'data': lista})
    except sqlite3.Error as e:
        return jsonify({'status': 'fail', 'mensaje': str(e)}) # str(e) = error pasado a cadena


