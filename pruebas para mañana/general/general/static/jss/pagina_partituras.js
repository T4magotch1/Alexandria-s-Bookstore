/*!
* Start Bootstrap - Shop Homepage v5.0.6 (https://startbootstrap.com/template/shop-homepage)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-shop-homepage/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project


const elementosProtegidos = document.getElementsByClassName('card-img-top'); // Es un contador de cuantos y que datos tiene cada iteracion de la clase 'card-img-top'

    // Itera sobre la colección de elementos
    for (let i = 0; i < elementosProtegidos.length; i++) { // va rotando sobre cada iteracion
        const elemento = elementosProtegidos[i]; //elemento obtiene el dato en la vuelta actual

      // Agrega el event listener para desactivar el clic derecho en cada elemento
        elemento.addEventListener('contextmenu', function(e) {
        e.preventDefault(); // y se anula el click derecho sobre cualquier imagen de la pagina 
        });
    }