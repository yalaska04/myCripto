from myCripto import app
from flask import render_template, jsonify, request, Response
from myCripto.dataaccess import DBmanager
from http import HTTPStatus
import sqlite3
import requests

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

@app.route('/api/v1/movimiento/<int:id>', methods=['GET'])
@app.route('/api/v1/movimiento', methods=['POST'])
def detalleMovimiento(id=None):
    try: 
        if request.method in ('GET'): 
            movimiento = dbManager.consultaUnaSQL("SELECT * FROM movimientos WHERE id = ?", [id])
            if movimiento:
                return jsonify({
                    # fijamos el diccionario de salid
                    "status": "success",
                    "movimiento": movimiento
                })
            else: 
                return jsonify({"status": "fail", "mensaje": "movimiento no encontrado"}), HTTPStatus.NOT_FOUND
        
        if request.method == 'POST': 
            dbManager.modificaTablaSQL("""
                INSERT INTO movimientos 
                        (date, time, moneda_from, cantidad_from, moneda_to, cantidad_to)
                VALUES (:date, :time, :moneda_from, :cantidad_from, :moneda_to, :cantidad_to)
                """, request.json)
            
            return jsonify({"status": "success", "mensaje": "registro creado"}), HTTPStatus.CREATED

    except sqlite3.Error as e: 
        return jsonify({"status": "fail", "mensaje": "Error en base de datos: {}".format(e)}), HTTPStatus.BAD_REQUEST

@app.route('/api/v1/par/<_from>/<_to>/<quantity>')
@app.route('/api/v1/par/<_from>/<_to>')
def par(_from, _to, quantity = 1.0):
    url = "https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY=f49776ff-0ede-431f-ae7d-bf19413c12b1".format(quantity, _from, _to)
    res = requests.get(url)
    return Response(res) # devuelve un json {"status":{...}, "data":{...}}


@app.route('/api/v1/status')
def status(): 
    return 