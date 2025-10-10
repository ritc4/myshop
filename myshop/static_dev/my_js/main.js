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
$(document).ready(function () {
  // Функция для переключения дополнительных полей доставки
  window.toggleAdditionalCol = function() { // Определяем функцию в глобальной области видимости
    var $select = $('#shipmethod'); // Получаем элемент select
    var $postalCodeCol = $('#postalCodeCol'); // Получаем блок postal_code
    var $passportNumberCol = $('#passportNumberCol'); // Получаем блок passport_number
    var $postalCodeInput = $('#postal_code'); // Получаем поле ввода postal_code
    var $passportNumberInput = $('#passport_number'); // Получаем поле ввода passport_number

    // Получаем текст выбранного метода доставки
    var selectedText = $select.find('option:selected').text();

    // Проверяем, выбран ли способ доставки "Почта"
    if (selectedText === "Почта") { 
      $postalCodeCol.show(); // Показываем блок postal_code
      $passportNumberCol.hide(); // Скрываем блок passport_number
      $postalCodeInput.attr('required', 'required'); // Устанавливаем поле postal_code обязательным
      $passportNumberInput.removeAttr('required'); // Убираем обязательность для passport_number
    } else if (selectedText === "ТК энергия") { // Проверяем, выбран ли способ доставки "ТК"
      $passportNumberCol.show(); // Показываем блок passport_number
      $postalCodeCol.hide(); // Скрываем блок postal_code
      $passportNumberInput.attr('required', 'required'); // Устанавливаем поле passport_number обязательным
      $postalCodeInput.removeAttr('required'); // Убираем обязательность для postal_code
    } else {
      $postalCodeCol.hide(); // Скрываем блок postal_code
      $passportNumberCol.hide(); // Скрываем блок passport_number
      $postalCodeInput.removeAttr('required'); // Убираем обязательность для postal_code
      $passportNumberInput.removeAttr('required'); // Убираем обязательность для passport_number
    }
  };

  // Вызываем функцию при загрузке страницы
  toggleAdditionalCol(); // Вызываем функцию при загрузке страницы

  // Обработчик изменения для select метода доставки
  $('#shipmethod').change(toggleAdditionalCol); // Обновляем поля при изменении метода доставки
});



// /* Функция автоматической отправки формы выбора количества товара в корзине */
$(document).ready(function() {
  $('.quantity-input').each(function() {
      const quantityInput = $(this);
      const updateForm = quantityInput.closest('.update-form'); // Найти ближайшую форму

      quantityInput.on('input', function() {
          console.log("Изменение значения: ", this.value); // Проверяем, срабатывает ли событие
          updateForm.submit(); // Отправляем форму
      });
  });
});


// Обработчик события изменения для выпадающего списка Modal окна category_page.html
$(document).ready(function() {
  // Инициализация отображения цены при загрузке страницы для каждого продукта
  $('[id^="size-select_product_"]').each(function() {
      var sizeSelect = $(this);
      var productId = sizeSelect.attr('id').split('_').pop(); // Получаем ID продукта из ID селектора
      var priceDisplay = $('#price-display-' + productId);

      // Устанавливаем начальное значение цены
      var selectedOption = sizeSelect.find('option:selected');
      var price = selectedOption.length ? selectedOption.data('price') : null;
      priceDisplay.text(price ? price + ' ₽' : 'Цена недоступна');

      // Добавляем обработчик событий для изменения размера
      sizeSelect.on('change', function() {
          var selectedOption = $(this).find('option:selected');
          var price = selectedOption.length ? selectedOption.data('price') : null;
          priceDisplay.text(price ? price + ' ₽' : 'Цена недоступна');
      });
  });
});




// Обработчик события изменения для выпадающего списка окна product_page.html
$(document).ready(function() {
  // Инициализация отображения цены при загрузке страницы
  var sizeSelect = $('#size-select_product');
  var priceDisplay = $('#price-display');

  if (sizeSelect.length && priceDisplay.length) {
      // Получаем выбранный элемент и его цену
      var selectedOption = sizeSelect.find('option:selected');
      var price = selectedOption.length ? selectedOption.data('price') : null;

      // Устанавливаем начальное значение цены
      priceDisplay.text(price ? price + ' ₽' : 'Цена недоступна');
  }

  // Добавляем общий обработчик событий для изменения размера
  $(document).on('change', '#size-select_product', function() {
      var selectedOption = $(this).find('option:selected');
      var price = selectedOption.length ? selectedOption.data('price') : null;

      // Проверяем, есть ли выбранная опция и выводим соответствующую цену
      priceDisplay.text(price ? price + ' ₽' : 'Цена недоступна');
  });
});


// Обработчик события вывод полного описания новости news_page.html
$(document).ready(function() {
  window.toggleDescription = function(event, id) {
      event.preventDefault();
      const descriptionElement = $(`#full-description-${id}`);
      
      if (descriptionElement.css("display") === "none") {
          descriptionElement.css("display", "block");
          $(event.target).text("Скрыть");
      } else {
          descriptionElement.css("display", "none");
          $(event.target).text("Читать полностью");
      }
  };
});


// Обработчик события вывод сортировки по цене и названию продуктов в category_page.html
$(document).ready(function() {
  // Проверяем, существует ли элемент с ID 'name-price'
  const select = $('#name-price');
  
  if (select.length) {
      // Функция сортировки
      function sortProducts() {
          const selectedValue = select.val();

          // Получаем текущее значение per_page из URL
          const urlParams = new URLSearchParams(window.location.search);
          const perPage = urlParams.get('per_page') || 30; // Установите значение по умолчанию, если per_page не найден

          // Обновляем URL с параметрами сортировки и per_page
          window.location.href = `?sort=${encodeURIComponent(selectedValue)}&per_page=${encodeURIComponent(perPage)}`;
      }

      // Привязываем обработчик события
      select.on('change', sortProducts);
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



// Обработчик показать или скрыть выбор рейтинга в reviews_page.html
$(document).ready(function() {
  // Звёздный рейтинг
  $('.star-rating').each(function() {
      const $starRating = $(this);
      const $stars = $starRating.find('.star');
      const $inputField = $('#' + $starRating.data('field'));

      $stars.on('click', function() {
          const value = $(this).data('value');
          $inputField.val(value); // Устанавливаем значение рейтинга в скрытое поле

          $stars.removeClass('selected'); // Удаляем класс "selected" со всех звёзд
          for (let i = 0; i < value; i++) {
              $stars.eq(i).addClass('selected'); // Добавляем класс "selected" к выбранным звёздам
          }
          console.log('Star clicked:', value); // Для отладки
      });
  });

  // Добавление изображений
  const imagePreviewContainer = $('#image-preview-container');
  const imageInput = $('input[name="images"]');
  const addedImages = [];

  imageInput.on('change', function() {
      const files = this.files;

      for (let i = 0; i < files.length; i++) {
          const file = files[i];

          // Проверяем, есть ли уже это изображение в массиве
          if (addedImages.includes(file)) {
              alert('Это изображение уже добавлено!'); // Уведомление о дубликате
              continue; // Пропускаем добавление этого файла
          }

          const reader = new FileReader();
          reader.onload = function(event) {
              // Создаем контейнер для изображения и кнопки удаления
              const imageContainer = $('<div>').addClass('image-container').css({
                  display: 'inline-block',
                  position: 'relative',
                  margin: '10px'
              });

              // Создаем изображение
              const img = $('<img>').attr('src', event.target.result).css({
                height: '200px', // Фиксированная высота
                width: 'auto',   // Автоматическая ширина для сохранения пропорций
                objectFit: 'contain' // Сохраняем пропорции изображения
              }).addClass('image-preview');

              // Создаем кнопку удаления
              const removeButton = $('<button>').text('✖️').css({
                  position: 'absolute',
                  top: '5px',
                  right: '5px',
                  color: 'white',
                  border: 'none',
                  borderRadius: '50%',
                  cursor: 'pointer',
                  padding: '5px',
              });

              // Добавляем обработчик для кнопки удаления
              removeButton.on('click', function() {
                  const index = addedImages.indexOf(file);
                  if (index > -1) {
                      addedImages.splice(index, 1); // Удаляем изображение из массива
                  }
                  imageContainer.remove(); // Удаляем контейнер изображения
              });

              // Добавляем изображение и кнопку удаления в контейнер
              imageContainer.append(img).append(removeButton);
              imagePreviewContainer.append(imageContainer);
              addedImages.push(file); // Добавляем файл в массив
          };
          reader.readAsDataURL(file);
      }

      // Очищаем поле ввода после добавления
      $(this).val('');
  });

  // Валидация перед отправкой формы
  $('#reviewForm').on('submit', function(event) {
      let isValid = true;

      $('.star-rating').each(function() {
          const $inputField = $('#' + $(this).data('field'));
          if ($inputField.val() === '') {
              isValid = false;
              $inputField.next('.form-error').text('Пожалуйста, выберите рейтинг.').show();
          } else {
              $inputField.next('.form-error').hide();
          }
      });
      if (!isValid) {
        event.preventDefault(); // Если не валидно, предотвращаем отправку формы
        return;
    }

    // Создаем объект FormData
    const formData = new FormData(this);
    addedImages.forEach(image => {
        formData.append('images', image); // Добавляем загруженные изображения в FormData
    });

    // Отправка данных на сервер с использованием AJAX
    $.ajax({
        url: this.action,
        type: this.method,
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            console.log('Отзыв успешно отправлен'); // Для отладки
            $('#yourModalId').modal('hide'); // Закрываем модальное окно стандартным способом
            imagePreviewContainer.empty();
            addedImages.length = 0; // Очищаем массив добавленных изображений
            location.reload(); // Перезагрузка текущей страницы
        },
        error: function(error) {
            console.error('Ошибка при отправке отзыва:', error); // Для отладки
            alert('Произошла ошибка при отправке отзыва. Пожалуйста, попробуйте еще раз.'); // Уведомление об ошибке
        }
    });

    event.preventDefault(); // Предотвращаем стандартное поведение формы
});
});





// Обработчик показать фото профиля в profile.html///////////////////////////////////////
$(document).ready(function() {
  // Обработчик для выбора файла
  $('#id_photo').on('change', function(event) {
      const file = event.target.files[0];
      if (file) {
          const reader = new FileReader();
          reader.onload = function(e) {
              $('#profileImage').attr('src', e.target.result); // Устанавливаем изображение
          };
          reader.readAsDataURL(file);
          
          // Снимаем галочку с чекбокса, если файл выбран
          $('#photo-clear_id').prop('checked', false);
      }
  });
  // Обработчик для кнопки "Очистить изображение"
  $('#photo-clear_id').on('click', function() {
      $('#profileImage').attr('src', '/media/users/default.png'); // Устанавливаем изображение по умолчанию
      $('#id_photo').val(''); // Очищаем поле загрузки
  });
});





// Обработчик обноления и удаления товаров в корзине через Ajax в cart_page.html///////////////////////////////////////
$(document).ready(function() {
  console.log("jQuery загружен:", typeof $);
  console.log("Формы найдены:", $('.update-form').length, $('.remove-form').length);

  // AJAX для обновления количества
  $('.quantity-input').on('change', function() {
      console.log("Изменение количества, значение:", $(this).val());
      if ($(this).data('updating')) return;  // Пропустить, если обновляется программно
      $(this).closest('.update-form').trigger('submit');
  });

  $('.update-form').on('submit', function(e) {
      e.preventDefault();
      console.log("Перехват submit для update-form");
      
      var form = $(this);
      console.log("Отправка формы обновления:", form.serialize());
      
      $.ajax({
          type: 'POST',
          url: form.attr('action'),
          data: form.serialize(),
          headers: {'X-Requested-With': 'XMLHttpRequest'},
          success: function(response) {
              console.log("Успешный ответ сервера:", response);
              if (response.success) {
                  var row = form.closest('.cart-item-row');
                  var input = row.find('.quantity-input');
                  input.data('updating', true).val(response.quantity).data('updating', false);  // Обновляем без вызова change
                  row.find('.item-total-price').text(response.item_total_price + ' ₽');
                  $('.cart-total-price').text(response.cart_total_price + ' ₽');
              } else {
                  alert('Ошибка: ' + response.error);
              }
          },
          error: function(xhr, status, error) {
              console.log("Ошибка AJAX:", xhr.responseText, status, error);
              alert('Произошла ошибка при обновлении.');
          }
      });
  });

  // AJAX для удаления
  $('.remove-form').on('submit', function(e) {
      e.preventDefault();
      console.log("Перехват submit для remove-form");
      
      var form = $(this);
      console.log("Отправка формы удаления:", form.serialize());
      
      $.ajax({
          type: 'POST',
          url: form.attr('action'),
          data: form.serialize(),
          headers: {'X-Requested-With': 'XMLHttpRequest'},
          success: function(response) {
              console.log("Успешный ответ сервера:", response);
              if (response.success) {
                  var row = form.closest('.cart-item-row');
                  row.remove();
                  $('.cart-total-price').text(response.cart_total_price + ' ₽');
                  if (response.is_empty) {
                      $('tbody').prepend('<tr><td colspan="8"><div class="alert alert-warning" role="alert">Ваша корзина пуста. Пожалуйста, добавьте товары в корзину перед оформлением заказа.</div></td></tr>');
                      $('.total').hide();
                  }
              }
          },
          error: function(xhr, status, error) {
              console.log("Ошибка AJAX:", xhr.responseText, status, error);
              alert('Произошла ошибка при удалении.');
          }
      });
  });
});







// $(document).ready(function() {
//   {% for item in cart %}
//     // Обновление цены при изменении размера для каждого товара
//     $('#size-select_product-{{ item.product.id }}').on('change', function() {
//       var selectedOption = $(this).find('option:selected');
//       var price = selectedOption.data('price');
//       if (price) {
//         $('#price-display-{{ item.product.id }}').text(price + ' ₽');
//       }
//     });

//     // AJAX для добавления товара в корзину для каждого товара
//     $('#add-to-cart-form-{{ item.product.id }}').on('submit', function(e) {
//       e.preventDefault();
//       console.log("Перехват submit для add-to-cart-form-{{ item.product.id }}");

//       var form = $(this);
//       console.log("Отправка формы добавления:", form.serialize());

//       $.ajax({
//         type: 'POST',
//         url: form.attr('action'),
//         data: form.serialize(),
//         headers: {'X-Requested-With': 'XMLHttpRequest'},
//         success: function(response) {
//           console.log("Успешный ответ сервера:", response);
//           if (response.success) {
//             // Обновите количество в корзине, если нужно
//             location.reload();  // Или обновите конкретные элементы без перезагрузки
//           } else {
//             console.log('Ошибка:', response.error);
//           }
//         },
//         error: function(xhr, status, error) {
//           console.log("Ошибка AJAX:", xhr.responseText, status, error);
//         }
//       });
//     });
//   {% endfor %}
// });




