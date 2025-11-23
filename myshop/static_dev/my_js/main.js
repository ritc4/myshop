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



// Обработчик показать или скрыть выбор рейтинга в reviews_page.html новый
$(document).ready(function() {
  // Функция показа уведомления посередине экрана (без изменений)
  function showNotification(message, type = 'error', duration = 3000) {
    $('.notification-alert').remove();
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const notification = $(`
      <div class="notification-alert alert ${alertClass} text-center p-3 mb-0 shadow-lg" role="alert">
        ${message}
      </div>
    `).css({
      position: 'fixed',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      zIndex: '9999',
      maxWidth: '400px',
      width: '90%',
      opacity: '0',
      transition: 'opacity 0.3s ease-in-out',
      borderRadius: '8px'
    });
    $('body').append(notification);
    notification.animate({ opacity: 1 }, 300);
    setTimeout(function() {
      notification.animate({ opacity: 0 }, 300, function() {
        $(this).remove();
      });
    }, duration);
  }

  // Звёздный рейтинг (без изменений)
  $('.star-rating').each(function() {
      const $starRating = $(this);
      const $stars = $starRating.find('.star');
      const $inputField = $('#' + $starRating.data('field'));
      $stars.on('click', function() {
          const value = $(this).data('value');
          $inputField.val(value);
          $stars.removeClass('selected');
          for (let i = 0; i < value; i++) {
              $stars.eq(i).addClass('selected');
          }
          console.log('Star clicked:', value);
      });
  });

  // Новый обработчик: показать или скрыть выбор рейтинга
  // Предполагаем, что в HTML есть чекбокс с id="show-rating-checkbox" и контейнер с классом "star-rating-container" (или используем .star-rating напрямую)
  // Если чекбокс отмечен, показываем рейтинг; иначе скрываем
  $('#show-rating-checkbox').on('change', function() {
    const isChecked = $(this).is(':checked');
    $('.star-rating').toggle(isChecked);  // Показываем/скрываем все элементы с классом star-rating
    // Опционально: сбрасываем значения рейтинга при скрытии
    if (!isChecked) {
      $('.star-rating').find('input[type="hidden"]').val('');  // Сбрасываем скрытые поля рейтинга
      $('.star-rating').find('.star').removeClass('selected');  // Снимаем выделение звёзд
    }
  });

  // Константы для изображений (без изменений)
  const maxFileSize = 20 * 1024 * 1024;
  const maxFiles = 5;
  const maxTotalSize = 100 * 1024 * 1024;
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  const imagePreviewContainer = $('#image-preview-container');
  const imageInput = $('input[name="images"]');
  const addButton = $('#add-images-button');
  const removeAllButton = $('#remove-all-images-button');
  const addedImages = [];

  function hasImages() {
    return addedImages.length > 0;
  }

  function updateButtons() {
    if (hasImages()) {
      removeAllButton.show();
    } else {
      removeAllButton.hide();
    }
  }

  function resetAllPreviews() {
    imagePreviewContainer.animate({ opacity: 0 }, 200, function() {
      imagePreviewContainer.empty().css('opacity', '1');
    });
    addedImages.length = 0;
    imageInput.val('');
    updateButtons();
  }

  addButton.on('click', function() {
    imageInput.click();
  });

  removeAllButton.on('click', function() {
    if (confirm('Вы уверены, что хотите удалить все изображения?')) {
      resetAllPreviews();
    }
  });

  imageInput.on('change', function(event) {
    const files = this.files;
    if (!files.length) return;
    let validFiles = [];
    let hasErrors = false;
    let totalSize = addedImages.reduce((sum, f) => sum + f.size, 0);

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (!allowedTypes.includes(file.type)) {
        showNotification(`Файл "${file.name}" не является изображением в формате JPEG, PNG, GIF или WebP.`);
        hasErrors = true;
        continue;
      }
      if (file.size > maxFileSize) {
        showNotification(`Размер файла "${file.name}" превышает ${maxFileSize / (1024 * 1024)} MB.`);
        hasErrors = true;
        continue;
      }
      if (addedImages.some(existing => existing.name === file.name && existing.size === file.size)) {
        showNotification(`Изображение "${file.name}" уже добавлено!`);
        hasErrors = true;
        continue;
      }
      if (addedImages.length + validFiles.length >= maxFiles) {
        showNotification(`Максимум ${maxFiles} изображений.`);
        hasErrors = true;
        break;
      }
      if (totalSize + file.size > maxTotalSize) {
        showNotification(`Общий размер изображений превысит ${maxTotalSize / (1024 * 1024)} MB.`);
        hasErrors = true;
        continue;
      }
      totalSize += file.size;
      validFiles.push(file);
    }

    if (!validFiles.length && !hasErrors) return;

    validFiles.forEach(file => {
      const reader = new FileReader();
      reader.onload = function(e) {
        const imageContainer = $('<div>').addClass('image-container').css({
          display: 'inline-block',
          position: 'relative',
          margin: '10px',
          opacity: '0'
        });
        const img = $('<img>').attr('src', e.target.result).css({
          height: '200px',
          width: 'auto',
          objectFit: 'contain'
        }).addClass('image-preview');
        const removeButton = $('<button>').addClass('remove-single btn btn-sm btn-danger').attr('type', 'button').css({
          position: 'absolute',
          top: '5px',
          right: '5px',
          borderRadius: '50%',
          width: '20px',
          height: '20px',
          padding: '0',
          fontSize: '12px'
        }).html('&times;').data('file', file);

        imageContainer.append(img).append(removeButton);
        imagePreviewContainer.append(imageContainer);
        imageContainer.animate({ opacity: 1 }, 300);
        addedImages.push(file);
        updateButtons();
      };
      reader.onerror = function() {
        showNotification(`Ошибка чтения файла "${file.name}".`);
      };
      reader.readAsDataURL(file);
    });
    $(this).val('');
  });

  imagePreviewContainer.on('click', '.remove-single', function() {
    const fileToRemove = $(this).data('file');
    const index = addedImages.findIndex(f => f.name === fileToRemove.name && f.size === fileToRemove.size);
    if (index !== -1) {
      addedImages.splice(index, 1);
      $(this).parent().animate({ opacity: 0 }, 300, function() {
        $(this).remove();
        updateButtons();
      });
    }
  });

  // Валидация и отправка формы с защитой от повторной отправки
  let isSubmitting = false;  // Флаг для предотвращения повторной отправки
  $('#reviewForm').on('submit', function(event) {
    if (isSubmitting) return;  // Если уже отправляется, игнорируем
    let isValid = true;
    
    // Проверка текста отзыва
    const content = $('textarea[name="content"]').val().trim();
    if (!content) {
      showNotification('Пожалуйста, напишите текст отзыва.');
      isValid = false;
    }
    
    // Проверка рейтингов (только если рейтинг показан)
    if ($('#show-rating-checkbox').is(':checked')) {
      $('.star-rating').each(function() {
          const $inputField = $('#' + $(this).data('field'));
          if ($inputField.val() === '') {
              showNotification('Пожалуйста, установите все рейтинги.');
              isValid = false;
              return false;
          }
      });
    }
    
    // Убрана проверка изображений — отзыв может быть без них
    
    if (!isValid) {
      event.preventDefault();
      return;
    }
    
    isSubmitting = true;  // Устанавливаем флаг
    const formData = new FormData(this);
    addedImages.forEach(image => {
        formData.append('images', image);
    });
    $.ajax({
        url: this.action,
        type: this.method,
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
          console.log('Отзыв успешно отправлен');
          showNotification('Отзыв успешно отправлен!', 'success', 2000);
          $('#reviewsModal').modal('hide');
          resetAllPreviews();
          setTimeout(() => window.location.href = response.redirect_url, 500);
          isSubmitting = false;
      },
        error: function(error) {
            console.error('Ошибка:', error);
            showNotification('Ошибка при отправке. Попробуйте снова.');
            isSubmitting = false;  // Сбрасываем флаг после ошибки
        }
    });
    event.preventDefault();
  });

  // ДОБАВЛЕНО: Обработчик для перемещения фокуса при начале закрытия модала (исправляет aria-hidden ошибку)
  $('.modal').on('hide.bs.modal', function() {
    var triggerButton = $(this).data('triggerButton');
    if (triggerButton) {
      triggerButton.focus();  // Перемещаем фокус на кнопку, открывшую модал, ДО применения aria-hidden
    }
  });

  // ДОБАВЛЕНО: Сохраняем кнопку-триггер при открытии модала (адаптировано для reviewsModal; предположим, кнопка имеет класс или ID, например, '.open-reviews-modal')
  $('.open-reviews-modal').on('click', function() {  // Замени на реальный селектор кнопки, открывающей #reviewsModal
    $('#reviewsModal').data('triggerButton', $(this));
  });
});






// Обработчик показать фото профиля в profile.html/////////////////////////////////////// новый
$(document).ready(function() {
  // Функция показа уведомления посередине экрана
  function showNotification(message, type = 'error', duration = 3000) {
    $('.notification-alert').remove();
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const notification = $(`
      <div class="notification-alert alert ${alertClass} text-center p-3 mb-0 shadow-lg" role="alert">
        ${message}
      </div>
    `).css({
      position: 'fixed',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      zIndex: '9999',
      maxWidth: '400px',
      width: '90%',
      opacity: '0',
      transition: 'opacity 0.3s ease-in-out',
      borderRadius: '8px'
    });
    $('body').append(notification);
    notification.animate({ opacity: 1 }, 300);
    setTimeout(function() {
      notification.animate({ opacity: 0 }, 300, function() {
        $(this).remove();
      });
    }, duration);
  }

  // Константы
  const maxFileSize = 20 * 1024 * 1024; // 100 MB (синхронизировано с Nginx и сервером)
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  const defaultImageSrc = $('#profileImage').data('default-src'); // Берем из data-default-src

  // Функция проверки фото
  function hasPhoto() {
    const src = $('#profileImage').attr('src');
    return src && src !== defaultImageSrc;
  }

  // Функция сброса превью
  function resetPreview() {
    $('#profileImage').animate({ opacity: 0 }, 200, function() {
      $('#profileImage').attr('src', defaultImageSrc).attr('alt', 'Default User Photo');
      $('#profileImage').animate({ opacity: 1 }, 300);
    });
    $('#photo-clear_id').val('true');
    $('#id_photo').val('');
    $('#photoButton').text('Добавить фото').prop('disabled', false);
  }

  // Обработчик кнопки
  $('#photoButton').on('click', function() {
    if (hasPhoto()) {
      resetPreview();
    } else {
      $('#id_photo').click();
    }
  });

  // Обработчик выбора файла
  $('#id_photo').on('change', function(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Валидация типа
    if (!allowedTypes.includes(file.type)) {
      showNotification('Пожалуйста, выберите изображение в формате JPEG, PNG, GIF или WebP.');
      resetPreview();
      return;
    }
    // Валидация размера
    if (file.size > maxFileSize) {
      showNotification(`Размер файла не должен превышать ${maxFileSize / (1024 * 1024)} MB.`);
      resetPreview();
      return;
    }

    // Индикатор загрузки
    $('#photoButton').text('Загрузка...').prop('disabled', true);

    // Превью
    const reader = new FileReader();
    reader.onload = function(e) {
      $('#profileImage').attr('src', e.target.result).attr('alt', 'User Photo').css('opacity', '0').animate({ opacity: 1 }, 300);
      $('#photo-clear_id').val('false');
      $('#photoButton').text('Удалить фото').prop('disabled', false);
    };
    reader.onerror = function() {
      showNotification('Ошибка чтения файла. Попробуйте другой файл.');
      resetPreview();
    };
    reader.readAsDataURL(file);
  });

  // Инициализация
  if (!hasPhoto()) {
    $('#photoButton').text('Добавить фото');
  } else {
    $('#photoButton').text('Удалить фото');
  }
});









