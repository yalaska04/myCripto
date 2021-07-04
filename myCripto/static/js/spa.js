
let losMovimientos // creo variable
xhr = new XMLHttpRequest()

function gestionaRespuestaApiStatus() {
    if (this.readyState === 4 && this.status === 200) {
        const respuesta = JSON.parse(this.responseText)

        if (respuesta.status !== 'success') {
            alert("Error en servidor: "+ respuesta.mensaje)
            return
        }

    const total_invertido = respuesta.data.total_invetido
    const valor_actual = respuesta.data.valor_actual
    const resultado = valor_actual - total_invertido

    document.getElementById('invertido').value = total_invertido.toFixed(2) + " €"
    document.getElementById('valor_actual').value = valor_actual.toFixed(2) + " €"
    if (parseFloat(resultado) < 0) {
        document.getElementById('resultado').style = "color: #ff0000;"
        document.getElementById('resultado').value = resultado.toFixed(2) + " €"
    } else {document.getElementById('resultado').value = resultado.toFixed(2) + " €"}

    }
}

function gestionaRespuestaApiCoinMarket() {
    if (this.readyState === 4 && (this.status === 200 || this.status === 201)) {
        const respuesta = JSON.parse(this.responseText)

        if (respuesta.status.error_code !== 0) {
            alert("Error en servidor: "+ respuesta.error_message)
            return
        }
        
        const moneda_to = document.querySelector("#moneda_to").value
        const cantidad_to = respuesta.data.quote[moneda_to].price // cantidad en la moneda deseada
        if (moneda_to !== 'EUR') {
            document.getElementById('cantidad_to').value = cantidad_to.toFixed(8)
        } else {
            document.getElementById('cantidad_to').value = cantidad_to.toFixed(2)
        }
        
        }
}

function recibeRespuesta() { // para hacer el onload solo cuando hagamos petición
    if (this.readyState === 4 && (this.status === 200 || this.status === 201)) {
        const respuesta = JSON.parse(this.responseText)

        if (respuesta.status !== 'success') {
            alert("Error en servidor: "+ respuesta.mensaje)
            return
        }
        
        alert("Movimiento guardado")

        llamaApiMovimientos() // muéstrame los movimientos 
    }
}

function muestraMovimientos() { // Recibe la respuesta (URL) de llamadaAPI
    if(this.readyState === 4 && this.status === 200){
        const respuesta = JSON.parse(this.responseText) // Pasa de string a objeto JSON (respuesta es un objeto)

        if (respuesta.status !== 'success'){
            alert('Error en servidor: ' + respuesta.mensaje)
            return 
        }

        losMovimientos = respuesta.data // ya tengo guardado mis movimientos en la memoria de la página, incluido id. Puedo acceder a ellos.
        const tbody = document.querySelector(".tabla-movimientos tbody") // para meterlo en el html, en tbody
        tbody.innerHTML = "" // vacíame el tbody

        for(let i = 0; i < respuesta.data.length; i++) {
            const movimiento = respuesta.data[i]
            const fila = document.createElement("tr")

            const dentro = `
                <td>${movimiento.date}</td>
                <td>${movimiento.time}</td>
                <td>${movimiento.moneda_from}</td>
                <td>${movimiento.cantidad_from}</td>
                <td>${movimiento.moneda_to}</td>
                <td>${movimiento.cantidad_to}</td>
            `
            fila.innerHTML = dentro
            tbody.appendChild(fila)
        }
        llamaApiStatus()
    }
}

function validar_calcular(movimiento) {
    
    if (isNaN(movimiento.cantidad_from)) { 
        alert("Error: la cantidad ha de ser un número")
        return false
    }

    if (movimiento.cantidad_from <= 0) {
        alert("Error: la cantidad ha de ser positiva")
        return false
    }

    return true
}

function validar_guardar(movimiento) {

    if (!movimiento.moneda_from) {
        alert("Error: divisa inicial obligatoria")
        return false
    }

    if (!movimiento.moneda_to) {
        alert("Error: divisa final obligatoria")
        return false
    }

    if (!movimiento.cantidad_from) {
        alert("Error: cantidad From obligatoria")
        return false
    }

    if (movimiento.cantidad_from <= 0) {
        alert("Error: la cantidad ha de ser positiva")
        return false
    }

    if (!movimiento.cantidad_to) {
        alert("Error: cantidad To obligatoria")
        return false
    }

    return true
}

function llamaApiMovimientos() {
    xhr.open('GET', 'http://127.0.0.1:5000/api/v1/movimientos', true) // crea petición GET la URL
    xhr.onload = muestraMovimientos // func. que recibe la URL (API) enviada
    xhr.send() // envío la petición GET la URL 
}

function generateTime() {
    var time = new Date()
    time = time.getHours() + ":" + time.getMinutes() + ":" + time.getSeconds()
    return time
}

function generateDate() {

    var today = new Date() // objeto date que contiene fecha y hora
    var dd = String(today.getDate()).padStart(2, '0')
    var mm = String(today.getMonth() + 1).padStart(2, '0') //Enero es 0!
    var yyyy = String(today.getFullYear())

    today = dd + '/' + mm + '/' + yyyy // cadena
    return today
}

function capturaFormularioMovimiento() {
    
    const movimiento = {}
    
    movimiento.date = generateDate() 
    movimiento.time = generateTime()
    movimiento.moneda_from = document.querySelector("#moneda_from").value
    movimiento.moneda_to = document.querySelector("#moneda_to").value
    movimiento.cantidad_from = document.querySelector("#cantidad_from").value
    movimiento.cantidad_to = document.querySelector("#cantidad_to").value
    
    return movimiento
}

function llamaApiCreaMovimiento(ev){
    ev.preventDefault() 
    // cojo los datos pintados en el formulario para transformarlo que envío al servidor
    const movimiento = capturaFormularioMovimiento() // nuevos movimientos guardado en la memoria de la página

    if (!validar_guardar(movimiento)) { // validaciones
        return
    }

    id = document.querySelector("#idMovimiento").value
    xhr.open("POST", `http://127.0.0.1:5000/api/v1/movimiento`, true)
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8") // meto en la cabecera un json para que views sepa lo que esperar
    xhr.onload = recibeRespuesta
    xhr.send(JSON.stringify(movimiento))
}

function llamaApiCoinMarket(ev){
    
    ev.preventDefault() 

    const movimiento = capturaFormularioMovimiento() 

    if (!validar_calcular(movimiento)) { // validaciones
        return
    }

    xhr.open('GET', `http://127.0.0.1:5000/api/v1/par/${movimiento.moneda_from}/${movimiento.moneda_to}/${movimiento.cantidad_from}`)
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
    xhr.send()
    xhr.onload = gestionaRespuestaApiCoinMarket
    

}

function llamaApiStatus(){
    
    xhr.open('GET', 'http://127.0.0.1:5000/api/v1/status', true) 
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
    xhr.send()
    xhr.onload = gestionaRespuestaApiStatus 
     
}

function disableBtnFrom() {
    var select_moneda_from = document.getElementById("moneda_from")  // selecciona el select entero con todas las opciones

    for (let i = 0; i < select_moneda_from.options.length; i++){
        select_moneda_from.options[i].removeAttribute('disabled'); 
    }
    
    var x = document.getElementById("moneda_to").selectedIndex // índice del elegido
    select_moneda_from.options[x].setAttribute('disabled', true); // para desactivar btn, pulsado en From, en To

}

function disableBtnTo() {

    var select_moneda_to = document.getElementById("moneda_to")  // selecciona el select entero con todas las opciones

    for (let i = 0; i < select_moneda_to.options.length; i++){
        select_moneda_to.options[i].removeAttribute('disabled'); 
    }
    
    var x = document.getElementById("moneda_from").selectedIndex // índice del elegido
    select_moneda_to.options[x].setAttribute('disabled', true); // para desactivar btn, pulsado en From, en To

}

window.onload = function() {
// Lo que haya dentro de esta función se ejecutará cuando la pag haya terminado de cargarse
// La usamos para evitar que el JS se ejecute antes de que la html se renderiza --> daría ERROR
    llamaApiMovimientos()

    document.querySelector("#moneda_to")
        .addEventListener("change", disableBtnFrom)
    
    document.querySelector("#moneda_from")
        .addEventListener("change", disableBtnTo)
        
    document.querySelector("#guardar")
        .addEventListener("click", llamaApiCreaMovimiento) // recoge el evento "click" al pulsar ok
    
    document.querySelector("#calcular")
        .addEventListener("click", llamaApiCoinMarket)
    
    document.querySelector("#actualizar")
        .addEventListener("click", llamaApiStatus)
}