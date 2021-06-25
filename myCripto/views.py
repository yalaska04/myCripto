from myCripto import app
from flask import render_template, jsonify, request, Response
from myCripto.dataaccess import DBmanager
from http import HTTPStatus
import sqlite3
import requests
import json

dbManager = DBmanager(app.config.get('DATABASE'))

def calculaSaldo(moneda): 

    query_from = "SELECT ifnull(sum(cantidad_from), 0) as cantidad_from_global FROM movimientos WHERE moneda_from={};".format(str(moneda))
    query_to = "SELECT ifnull(sum(cantidad_to), 0) as  cantidad_to_global FROM movimientos WHERE moneda_to={};".format(str(moneda))

    dic_from = dbManager.consultaUnaSQL(query_from) # diccioanrio con la suma de cantidad_from(moneda)
    dic_to = dbManager.consultaUnaSQL(query_to) # diccionario con la suma de cantidad_to(moneda)
    dic_to.update(dic_from) # mete dic suma de cantidad_from(€) en dic suma de cantidad_to(moneda)

    saldo = dic_to['cantidad_to_global'] - dic_to['cantidad_from_global']
    
    return saldo 

def calculaInvertido(moneda):
    
    query_from = "SELECT ifnull(sum(cantidad_from), 0) as cantidad_from_global FROM movimientos WHERE moneda_from={};".format(str(moneda))
    dic_from = dbManager.consultaUnaSQL(query_from)
    invertido = dic_from['cantidad_from_global']

    return invertido
    

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
            
            dic_id = dbManager.consultaUnaSQL("SELECT  last_insert_rowid() as last_id;")
        
            return jsonify({"status": "success", "id": dic_id['last_id']}), HTTPStatus.CREATED

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
    
    status = {'saldos':{}, 'invertido': {} , 'valor_criptos_en_euros':{}, 'valor_criptos_en_euros_global': {}, 'valor_actual': {}}
    
    divisas = ['"EUR"', '"BTC"', '"ETH"', '"LTC"', '"BNB"', '"EOS"', '"XLM"',
             '"TRX"', '"XRP"', '"BCH"', '"USDT"', '"BSV"', '"ADA"']
    
    # SALDO: saldo = cantidad_to_global - cantidad_from_global

    for divisa in divisas: 
        divisa_sin_comillas_dobles = divisa.replace('"','')
        status['saldos'][divisa_sin_comillas_dobles]=calculaSaldo(divisa)
    
    # INVERTIDO: invertido = cantidad_from_global(€)

    status['invertido'] = calculaInvertido('"EUR"')

    # VALOR GLOBAL DE CRIPTOS EN EUROS: valor_criptos_en_euros_global 
        # 1) saldo_cripto_en_cripto = cantidad_to_global - cantidad_from_global
        # 2) Pasar de saldo_cripto_en_cripto => saldo_cripto_en_euros usando API
        # 3) Sumar todos para sacar el global 

    valor_criptos_en_euros_global = 0 
    for divisa in divisas: 
        divisa_sin_comillas_dobles = divisa.replace('"','') 

        saldo=int(calculaSaldo(divisa))
        if saldo > 0:
            url = "https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={}&symbol={}&convert={}&CMC_PRO_API_KEY=f49776ff-0ede-431f-ae7d-bf19413c12b1".format(calculaSaldo(divisa), divisa_sin_comillas_dobles, 'EUR')
            res = requests.get(url)
            dic_res = res.json()
            valor_cripto_en_euros = dic_res['data']['quote']['EUR']['price']
            
            status['valor_criptos_en_euros'][divisa_sin_comillas_dobles] = round(valor_cripto_en_euros,2)
            
            valor_criptos_en_euros_global += valor_cripto_en_euros

        else: 
            status['valor_criptos_en_euros'][divisa_sin_comillas_dobles] = "Saldo insuficiente"
        
    status['valor_criptos_en_euros_global'] = round(valor_criptos_en_euros_global,2)
    
    # VALOR ACTUAL: valor_actual = invertido + saldo + vac
    
    valor_actual = status['invertido'] + status['valor_criptos_en_euros_global'] + status['saldos']['EUR']
    status['valor_actual'] = round(valor_actual, 2)
    
    try:
        return jsonify({'status': 'success', 'data': status})
    except sqlite3.Error as e:
        return jsonify({'status': 'fail', 'mensaje': str(e)}) # str(e) = error pasado a cadena


    # return jsonify({"status": "success", "data": {"invertido" = invertido, "valor actual" = valor_actual}})
    