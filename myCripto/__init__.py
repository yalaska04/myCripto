from flask import Flask 

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config') # Crea en app un atributo que se llama config que lleva la ruta

from  myCripto.views import * 