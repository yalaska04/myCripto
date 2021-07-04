from os import error
from myCripto import app
from flask import render_template, jsonify, request, Response
from myCripto.dataaccess import DBmanager
from http import HTTPStatus
from datetime import datetime
import sqlite3
import requests
import json

criptoMonedas = ['BTC', 'ETH', 'LTC', 'BNB', 'EOS', 'XLM',
             'TRX', 'XRP', 'BCH', 'USDT', 'BSV', 'ADA']

dbManager = DBmanager(app.config.get('DATABASE'))
ApiKey = app.config.get('APIKEY')

def calculaSaldo(moneda): 

    query_from = f"SELECT ifnull(sum(cantidad_from), 0) as cantidad_from_global FROM movimientos WHERE moneda_from='{moneda}';"
    query_to = f"SELECT ifnull(sum(cantidad_to), 0) as  cantidad_to_global FROM movimientos WHERE moneda_to='{moneda}';"

    dic_from = dbManager.consultaUnaSQL(query_from) # diccioanrio con la suma de cantidad_from(moneda)
    dic_to = dbManager.consultaUnaSQL(query_to) # diccionario con la suma de cantidad_to(moneda)
    dic_to.update(dic_from) # mete dic suma de cantidad_from(€) en dic suma de cantidad_to(moneda)
   
    saldo = dic_to['cantidad_to_global'] - dic_to['cantidad_from_global']
    
    return saldo 

def totalInvertido(moneda): 
    query_from = f"SELECT ifnull(sum(cantidad_from), 0) as cantidad_from_global FROM movimientos WHERE moneda_from='{moneda}';"
    dic_from = dbManager.consultaUnaSQL(query_from)
    totalInvertido = dic_from['cantidad_from_global']
    return totalInvertido

@app.route('/')
def listaMovimientos(): 
    return render_template('spa.html')

@app.route('/api/v1/movimientos') # Ruta de las APIs
def movimientosAPI():
    query = "SELECT * FROM movimientos ORDER BY id DESC;"

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
                return jsonify({"status": "success", "movimiento": movimiento}), HTTPStatus.OK
            else: 
                return jsonify({"status": "fail", "mensaje": "movimiento no encontrado"}), HTTPStatus.NOT_FOUND
        
        if request.method == 'POST':
            data = request.json  
            data['date'] = datetime.now().strftime("%d/%m/%Y")
            data['time'] = datetime.now().strftime("%H:%M:%S")

            moneda_to = data['moneda_to']
            moneda_from = data['moneda_from']
            cantidad_from = float(data['cantidad_from'])
            saldo = float(calculaSaldo(moneda_from))
            
            if moneda_from != 'EUR':
                if saldo < cantidad_from: 
                    return jsonify({'status': 'fail', 'mensaje': f'Saldo de {moneda_from} insuficiente'})
            
            if moneda_from == moneda_to: 
                return jsonify({'status': 'fail', 'mensaje': 'From y To deben ser distintos'})

            dbManager.modificaTablaSQL("""
                INSERT INTO movimientos 
                        (date, time, moneda_from, cantidad_from, moneda_to, cantidad_to)
                VALUES (:date, :time, :moneda_from, :cantidad_from, :moneda_to, :cantidad_to)
                """, data)
            
            dic_id = dbManager.consultaUnaSQL("SELECT id  FROM movimientos ORDER BY id DESC LIMIT 1;")
        
            return jsonify({"status": "success", "id": dic_id['id']}), HTTPStatus.CREATED

    except sqlite3.Error as e: 
        return jsonify({"status": "fail", "mensaje": f"Error en base de datos: {e}"}), HTTPStatus.BAD_REQUEST

@app.route('/api/v1/par/<_from>/<_to>/<quantity>')
@app.route('/api/v1/par/<_from>/<_to>')
def par(_from, _to, quantity = 1.0):
    try:
        if float(quantity) < 0: 
            return  jsonify({"status": "fail", "mensaje": "Cantidad debe ser positiva"})

        url = f"https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={quantity}&symbol={_from}&convert={_to}&CMC_PRO_API_KEY={ApiKey}"
        res = requests.get(url)
        return Response(res) # devuelve un json {"status":{...}, "data":{...}}
    
    except:
        return jsonify({'status': 'fail', 'mensaje': "Error al conectar con la API"}), HTTPStatus.BAD_REQUEST

@app.route('/api/v1/status')
def status(): 
    
    try:
        data = {'total_invetido': {} , 'valor_criptos_en_euros':{}, 'valor_actual': {}}

        valor_criptos_en_euros_global = 0 
        saldo_euros = calculaSaldo('EUR')
        total_invertido_euros = totalInvertido('EUR')
        
        for cripto in criptoMonedas: 
            saldo=float(calculaSaldo(cripto))

            if saldo > 0:
                url = f"https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={calculaSaldo(cripto)}&symbol={cripto}&convert={'EUR'}&CMC_PRO_API_KEY={ApiKey}"
                res = requests.get(url)
                dic_res = res.json()
                try:
                    valor_cripto_en_euros = dic_res['data']['quote']['EUR']['price']
                
                    data['valor_criptos_en_euros'][cripto] = valor_cripto_en_euros
                
                    valor_criptos_en_euros_global += round(valor_cripto_en_euros,2)
                except:
                    error = dic_res['status']['error_message']
                    return jsonify({'status': 'fail', 'mensaje': error})
            else: 
                data['valor_criptos_en_euros'][cripto] = 0
        
        data['total_invetido'] = total_invertido_euros
        data['valor_actual'] = total_invertido_euros + saldo_euros + valor_criptos_en_euros_global
        
        return jsonify({'status': 'success', 'data': data}), HTTPStatus.OK

    except sqlite3.Error as e:
        return jsonify({'status': 'fail', 'mensaje': str(e)}), HTTPStatus.BAD_REQUEST 
