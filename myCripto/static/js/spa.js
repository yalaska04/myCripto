
function muestraMovimientos() { // Recibe la respuesta (URL) de llamadaAPI
    if(this.readyState === 4 && this.status === 200){
        const respuesta = JSON.parse(this.responseText) // Pasa de JSON a string

        if (respuesta.status !== 'success'){
            alert('Se ha producido un error en la consulta de movimientos')
            return 
        }

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
            const tbody = document.querySelector(".tabla-movimientos tbody") // para meterlo en el html, en tbody
            tbody.appendChild(fila)
        }
    }
}


xhr = new XMLHttpRequest()
xhr.onload = muestraMovimientos // fun que recibe la URL (API) enviada

function llamaApiMovimientos() {
    xhr.open('GET', 'http://127.0.0.1:5000/api/v1/movimientos') // crea la URL
    xhr.send() // envío la URL 
}

window.onload = function() {
// Lo que haya dentro de esta función se ejecutará cuando la pag haya terminado de cargarse
// La usamos para evitar que el JS se ejecute antes de que la html se renderiza --> daría ERROR
    llamaApiMovimientos()

}