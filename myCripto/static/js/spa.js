let losMovimientos // creo variable
xhr = new XMLHttpRequest()

function recibeRespuesta() { // para hacer el onload solo cuando hagamos petición
    if (this.readyState === 4 && (this.status === 200 || this.status === 201)) {
        const respuesta = JSON.parse(this.responseText)

        if (respuesta.status !== 'success') {
            alert("Se ha producido un error en acceso a servidor "+ respuesta.mensaje)
            return
        }

        alert(respuesta.mensaje)

        llamaApiMovimientos() // muéstrame los movimientos 
    }
}


function detallaMovimiento(id) {
// función que al pulsar una fila te captura los atributos y los plasma en el formulario
    let movimiento // recupero la posición del elemento que quiero a través de la id 
    for (let i=0; i<losMovimientos.length; i++) {
        const item = losMovimientos[i]
        if (item.id == id ) {
            movimiento = item
            break
        }
    }
    
    if (!movimiento) return 
    document.querySelector("#idMovimiento").value = id // para guardar el id 
    document.querySelector("#moneda_from").value = movimiento.moneda_from // apunta a id y le asigno un valor
    document.querySelector("#cantidad_from").value = movimiento.cantidad_from.toFixed(2)
    document.querySelector("#moneda_to").value = movimiento.moneda_to
}


function muestraMovimientos() { // Recibe la respuesta (URL) de llamadaAPI
    if(this.readyState === 4 && this.status === 200){
        const respuesta = JSON.parse(this.responseText) // Pasa de string a objeto JSON (respuesta es un objeto)

        if (respuesta.status !== 'success'){
            alert('Se ha producido un error en la consulta de movimientos')
            return 
        }

        losMovimientos = respuesta.data // ya tengo guardado mis movimientos en la memoria de la página, incluido id. Puedo acceder a ellos.
        const tbody = document.querySelector(".tabla-movimientos tbody") // para meterlo en el html, en tbody
        tbody.innerHTML = "" // vacíame el tbody

        for(let i = 0; i < respuesta.data.length; i++) {
            const movimiento = respuesta.data[i]
            const fila = document.createElement("tr")

            fila.addEventListener("click", () => { // El () hace que se ejecute la función solo cuando se haga click, sin el se ejecutaría cuando se lea la linea
                detallaMovimiento(movimiento.id)
            })

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
    }
}


function llamaApiMovimientos() {
    xhr.open('GET', 'http://127.0.0.1:5000/api/v1/movimientos', true) // crea petición GET la URL
    xhr.onload = muestraMovimientos // func. que recibe la URL (API) enviada
    xhr.send() // envío la petición GET la URL 
}

window.onload = function() {
// Lo que haya dentro de esta función se ejecutará cuando la pag haya terminado de cargarse
// La usamos para evitar que el JS se ejecute antes de que la html se renderiza --> daría ERROR
    llamaApiMovimientos()
    
    document.querySelector("#aceptar")
        .addEventListener("click", (ev) => { // recoge el evento "click" al pulsar ok
            ev.preventDefault() 
            // cojo los datos pintados en el formulario para transformarlo que envío al servidor
            const movimiento = {}
            movimiento.moneda_from = document.querySelector("#moneda_from").value
            movimiento.moneda_to = document.querySelector("#moneda_to").value
            movimiento.cantidad_from = document.querySelector("#cantidad_from").value
            movimiento.cantidad_to = document.querySelector("#cantidad_to").value

            id = document.querySelector("#idMovimiento").value
            xhr.open("POST", `http://127.0.0.1:5000/api/v1/movimiento`, true)
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8") // meto en la cabecera un json para que views sepa lo que esperar
            xhr.onload = recibeRespuesta
            xhr.send(JSON.stringify(movimiento))
        }) 
}