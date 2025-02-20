$(document).ready(function () {
  // Обработка события прокрутки
  $(window).scroll(function () {
    if ($(this).scrollTop() > 300) {
      $("#top").fadeIn(); // Показываем кнопку "вверх"
    } else {
      $("#top").fadeOut(); // Скрываем кнопку "вверх"
    }
  });

  // Обработка клика по кнопке "вверх"
  $("#top").click(function () {
    $("html, body").animate({ scrollTop: 0 }, 500); // Прокручиваем к верху страницы
    return false; // Предотвращаем стандартное поведение
  });

  // Инициализация карусели Owl Carousel
  $(".own-carousel-full").owlCarousel({
    margin: 20,
    responsive: {
      0: {
        items: 1, // Для экранов шириной 0px и выше
      },
      768: {
        items: 2, // Для экранов шириной 768px и выше
      },
      992: {
        items: 3, // Для экранов шириной 992px и выше
      },
    },
  });
});


const offcanvasCartEl = document.getElementById("offcanvasCart");
const offcanvasCart = new bootstrap.Offcanvas(offcanvasCartEl);
document.getElementById('cart-open').addEventListener('click',(e) =>{
    e.preventDefault();
    offcanvasCart.toggle();

});

document.querySelectorAll('.closecart').forEach(item =>{
    item.addEventListener('click',(e) =>{
        e.preventDefault();
        offcanvasCart.hide();
        let href = item.href.split("#").pop();
        document.getElementById(href).scrollIntoView();
    });
});



/* Показываем дополнительный блок доставки товара*/
function toggleAdditionalCol() {
    var select = document.getElementById('shipmethod'); // Получаем элемент select
    var additionalCol = document.getElementById('additionalCol'); // Получаем дополнительный блок

    // Проверяем, выбран ли способ доставки, который требует дополнительной информации
    if (select.value === "3"|| select.value === "4" || select.value === "5"|| select.value === "6"|| select.value === "7"|| select.value === "8") { // Например, если выбрана СДЭК
        additionalCol.style.display = 'block'; // Показываем блок
    } else {
        additionalCol.style.display = 'none'; // Скрываем блок
    }
}



// /* Функция автоматической отправки формы выбора количества товара в корзине */
document.addEventListener('DOMContentLoaded', function() {
  const quantityInputs = document.querySelectorAll('.quantity-input');
  
  quantityInputs.forEach(function(quantityInput) {
      const updateForm = quantityInput.closest('.update-form'); // Найти ближайшую форму
      
      quantityInput.addEventListener('input', function() {
          console.log("Изменение значения: ", this.value); // Проверяем, срабатывает ли событие
          updateForm.submit(); // Отправляем форму
      });
  });
});
