# Proyecto Fin Bootcamp

Crear aplicación web que resgistre movimientos de criptomonedas 

## Instalación 

1. Crear entorno virtual y activarlo

* Crear

```python
    python3 -m venv venv 
```

* Activar 
    
    - en Mac

    
    ```python
    . venv/bin/activate
    ```

    - en Windows

    ```python
    . venv/Scripts/activate
    ```

2. Instalar dependencias

```python
pip install -r requirements.txt
```

3. Crear variables de entorno 

    * Duplicar el finchero `.env_template`
    * Renombrar la copia a `.env`
    * Informar FLASK_ENV a elegir entre `development` y `production` 
    

4. Crear fichero de configuración 

    * Duplicar el fichero `config_template.py`
    * Renombrar la copia a `config.py`
    * Informar APIKEY. Para obtener tu apikey [aqui](https://coinmarketcap.com/api/)
    * Informar el fichero de bases de datos DATABASE. La ruta debe estar dentro del proyecto.
    

5. Crear base de datos ejecutando el fichero `migrations/initial.sql`

    * Puedes hacerlo con un cliente gráfico o con sqlite3
    * Ejecutar lo siguiente

```python
sqlite3 <ruta al fichero puesto en config.py>
.read <ruta relativa a migrations/initial.sql>
.tables
.q
```

## Ejecutar en local 

Simplemente escribir 

```python
flask run
```
