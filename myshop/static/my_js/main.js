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
    if (select.value === "2"||select.value === "6"|| select.value === "7" || select.value === "8"|| select.value === "9"|| select.value === "10") { // Например, если выбрана СДЭК
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


// Обработчик события изменения для выпадающего списка Modal окна category_page.html
document.addEventListener('DOMContentLoaded', function() {
  // Инициализация отображения цены при загрузке страницы для каждого продукта
  document.querySelectorAll('[id^="size-select_product_"]').forEach(function(sizeSelect) {
      var productId = sizeSelect.id.split('_').pop(); // Получаем ID продукта из ID селектора
      var priceDisplay = document.getElementById('price-display-' + productId);

      // Устанавливаем начальное значение цены
      var selectedOption = sizeSelect.options[sizeSelect.selectedIndex];
      var price = selectedOption ? selectedOption.getAttribute('data-price') : null;
      priceDisplay.innerText = price ? price + ' ₽' : 'Цена недоступна';

      // Добавляем обработчик событий для изменения размера
      sizeSelect.addEventListener('change', function() {
          var selectedOption = this.options[this.selectedIndex];
          var price = selectedOption ? selectedOption.getAttribute('data-price') : null;
          priceDisplay.innerText = price ? price + ' ₽' : 'Цена недоступна';
      });
  });
});

// Обработчик события изменения для выпадающего списка окна product_page.html
document.addEventListener('DOMContentLoaded', function() {
  // Инициализация отображения цены при загрузке страницы
  var sizeSelect = document.getElementById('size-select_product');
  var priceDisplay = document.getElementById('price-display');

  if (sizeSelect && priceDisplay) {
      // Получаем выбранный элемент и его цену
      var selectedOption = sizeSelect.options[sizeSelect.selectedIndex];
      var price = selectedOption ? selectedOption.getAttribute('data-price') : null;

      // Устанавливаем начальное значение цены
      priceDisplay.innerText = price ? price + ' ₽' : 'Цена недоступна';
  }

  // Добавляем общий обработчик событий для изменения размера
  document.addEventListener('change', function(event) {
      if (event.target.id === 'size-select_product') {
          var selectedOption = event.target.options[event.target.selectedIndex];
          var price = selectedOption ? selectedOption.getAttribute('data-price') : null;

          // Получаем элемент для отображения цены по его ID
          if (priceDisplay) {
              // Проверяем, есть ли выбранная опция и выводим соответствующую цену
              priceDisplay.innerText = price ? price + ' ₽' : 'Цена недоступна';
          }
      }
  });
});


// Обработчик события вывод полного описания новости news_page.html
document.addEventListener('DOMContentLoaded', function() {
  window.toggleDescription = function(event, id) {
      event.preventDefault();
      const descriptionElement = document.getElementById(`full-description-${id}`);
      if (descriptionElement.style.display === "none") {
          descriptionElement.style.display = "block";
          event.target.textContent = "Скрыть";
      } else {
          descriptionElement.style.display = "none";
          event.target.textContent = "Читать полностью";
      }
  };
});


// Обработчик события вывод сортировки по цене и названию продуктов в category_page.html
// function sortProducts() {
//   const select = document.getElementById('name-price');
//   const selectedValue = select.value;

//   // Получаем текущее значение per_page из URL
//   const urlParams = new URLSearchParams(window.location.search);
//   const perPage = urlParams.get('per_page') || 30; // Установите значение по умолчанию, если per_page не найден

//   // Обновляем URL с параметрами сортировки и per_page
//   window.location.href = `?sort=${encodeURIComponent(selectedValue)}&per_page=${encodeURIComponent(perPage)}`;
// }

// document.addEventListener('DOMContentLoaded', function() {
//   const select = document.getElementById('name-price');
//   select.addEventListener('change', sortProducts); // Привязываем обработчик события
// });


document.addEventListener('DOMContentLoaded', function() {
  // Проверяем, существует ли элемент с ID 'name-price'
  const select = document.getElementById('name-price');
  
  if (select) {
      // Функция сортировки
      function sortProducts() {
          const selectedValue = select.value;

          // Получаем текущее значение per_page из URL
          const urlParams = new URLSearchParams(window.location.search);
          const perPage = urlParams.get('per_page') || 30; // Установите значение по умолчанию, если per_page не найден

          // Обновляем URL с параметрами сортировки и per_page
          window.location.href = `?sort=${encodeURIComponent(selectedValue)}&per_page=${encodeURIComponent(perPage)}`;
      }

      // Привязываем обработчик события
      select.addEventListener('change', sortProducts);
  }
});



// Обработчик события вывод сортировки по количеству продуктов в category_page.html
function updatePerPage(value) {
  console.log('Updating per_page to:', value); // Проверка значения
  const newUrl = new URL(window.location.href);
  newUrl.searchParams.set('per_page', value);
  newUrl.searchParams.set('page', 1); // Сбрасываем страницу на 1
  console.log('New URL:', newUrl.toString()); // Проверка нового URL
  window.location.href = newUrl.toString();
}