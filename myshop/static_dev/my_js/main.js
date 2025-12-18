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









// Обработчик показать или скрыть выбор рейтинга в reviews_page.html новый
$(document).ready(function() {
  // Toast-подобные уведомления (то же, что у вас)
  function showNotification(message, type = 'error', duration = 3000) {
    $('.notification-alert').remove();
    const alertClass = type === 'success' ? 'alert-success' : type === 'warning' ? 'alert-warning' : type === 'info' ? 'alert-info' : 'alert-danger';
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

  // ИСПРАВЛЕНО: Сброс превью и всех полей формы (для использования при закрытии модала)
  function resetAllPreviews() {
    imagePreviewContainer.empty();
    addedImages = [];
    totalSize = 0;  // Сброс общего размера
    updateButtons();
    updateImageCounter();
    // ДОБАВЛЕНО: Очистка текста отзыва, рейтингов и других полей
    $('textarea[name="content"]').val('');
    $('.star-rating').each(function() {
      const $starRating = $(this);
      const $stars = $starRating.find('.star');
      const $inputField = $('#' + $starRating.data('field'));
      $inputField.val('');  // Сброс скрытого поля рейтинга
      $stars.removeClass('selected');  // Убираем визуальные звёзды
    });
  }

  // Звёздный рейтинг — оставьте как есть
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
      });
  });

  // Константы изображений (сжатие до 5MB/client)
  const maxFileSize = 5 * 1024 * 1024; // 5 MB
  const maxFiles = 5;
  const maxTotalSize = 25 * 1024 * 1024; // 25 MB total
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  const imagePreviewContainer = $('#image-preview-container');
  const imageInput = $('input[name="images"]');
  const addButton = $('#add-images-button');
  const removeAllButton = $('#remove-all-images-button');
  let addedImages = []; // Массив сжатых Blob
  let totalSize = 0; // Общий размер добавленных изображений

  function hasImages() { return addedImages.length > 0; }
  function updateButtons() {
    removeAllButton.toggle(hasImages());
  }
  function createPreview(file, index) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const container = $('<div>').addClass('image-container').css({ position: 'relative', margin: '10px' });
      const img = $('<img>').attr('src', e.target.result).css({ height: '200px', width: 'auto', objectFit: 'contain' });
      const removeBtn = $('<button>').addClass('remove-single btn btn-sm btn-danger').css({ position: 'absolute', top: 5, right: 5 }).html('&times;').data('file', file);
      container.append(img).append(removeBtn).appendTo(imagePreviewContainer).animate({ opacity: 1 }, 300);
    };
    reader.readAsDataURL(file);
  }
  function updateImageCounter() { $('#image-counter').text(`${addedImages.length}/${maxFiles}`); }

  addButton.on('click', () => imageInput.click());

  // Сжатие через Compressor.js перед добавлением
  imageInput.on('change', (event) => {
    const files = Array.from(event.target.files);
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (addedImages.length >= maxFiles) { 
        showNotification(`Максимум ${maxFiles} изображений.`, 'warning'); 
        continue; 
      }
      if (addedImages.some(img => img.name === file.name)) { 
        showNotification(`${file.name} уже добавлен.`, 'warning'); 
        continue; 
      }
      if (totalSize + file.size > maxTotalSize) {
        showNotification(`Общий размер изображений превысит ${maxTotalSize / (1024 * 1024)} MB.`);
        continue;
      }
      if (file.size > maxFileSize) { 
        showNotification(`Размер файла ${Math.floor(file.size / 1e6)}MB что превышает 5MB.`, 'error'); 
        continue; 
      }
      if (!allowedTypes.includes(file.type)) {
        showNotification(`Файл "${file.name}" не является изображением в формате JPEG, PNG, GIF или WebP.`);
        continue;
      }

      new Compressor(file, {
        quality: 0.8,  // 80%
        maxWidth: 1920,  // Подгонка под размер (до обработки будет резать сервер)
        maxHeight: 1920,
        convertSize: 1e6,
        success(compressedFile) {
          totalSize += compressedFile.size;
          addedImages.push(compressedFile);
          createPreview(file, addedImages.length - 1);
          showNotification(`${file.name}: Добавлено.`, 'success', 2000);
          updateImageCounter();
          updateButtons();  // ИСПРАВЛЕНО: Добавлен вызов для показа кнопки "Удалить все" после добавления изображения(ий)
        },
        error(err) { showNotification('Ошибка сжатия.', 'warning'); }
      });
    }
    imageInput.val('');
  });

  imagePreviewContainer.on('click', '.remove-single', function() {
    const index = imagePreviewContainer.find('.image-container').index($(this).parent());
    if (index !== -1) { 
      totalSize -= addedImages[index].size;
      addedImages.splice(index, 1); 
      $(this).parent().remove(); 
      updateButtons(); 
      updateImageCounter(); 
    }
  });

  removeAllButton.on('click', () => {
    imagePreviewContainer.empty(); 
    addedImages = []; 
    totalSize = 0;
    updateButtons(); 
    updateImageCounter(); 
  });

  // Валидация формы с прогрессом
  let isSubmitting = false;
  $('#reviewForm').on('submit', function(event) {
    if (isSubmitting) return;
    const content = $('textarea[name="content"]').val().trim();
    if (!content) { showNotification('Введите текст отзыва.'); event.preventDefault(); return; }
    let ratingsValid = true;
    // ИСПРАВЛЕНО: Используем function() вместо () =>, чтобы this работал правильно,и проверка рейтингов проходила
    $('.star-rating').each(function() { 
      const val = $('#' + $(this).data('field')).val(); 
      if (!val || val < 1) ratingsValid = false; 
    });
    if (!ratingsValid) { showNotification('Заполните рейтинги.'); event.preventDefault(); return; }

    isSubmitting = true;
    const submitBtn = $('#submit-review-btn').prop('disabled', true).text('Отправляется...');
    const formData = new FormData(this);
    addedImages.forEach(img => formData.append('images', img));

    $.ajax({
      url: this.action,
      type: this.method,
      data: formData,
      processData: false,
      contentType: false,
      xhr: () => {
        const xhr = new XMLHttpRequest();
        let lastProgress = 0;
        xhr.upload.addEventListener("progress", e => {
          if (e.lengthComputable) {
            const percent = Math.round(e.loaded / e.total * 100);
            if (percent > lastProgress + 10) { showNotification(`Загрузка: ${percent}%...`, 'info', 1500); lastProgress = percent; }
          }
        });
        return xhr;
      },
      success(response) {
        if (response.success) { 
          showNotification('Сохранено!', 'success', 3000); 
          $('#reviewsModal').modal('hide'); 
          resetAllPreviews();  // Теперь определено — сбрасывает изображения
          setTimeout(() => location.href = response.redirect_url, 500); 
        } else showNotification(response.message, 'error');
        isSubmitting = false; submitBtn.prop('disabled', false).text('Отправить отзыв');
      },
      error(xhr) { showNotification('Ошибка: ' + (xhr.status || 'timeout'), 'error'); isSubmitting = false; submitBtn.prop('disabled', false).text('Отправить отзыв'); },
      timeout: 60000
    });
    event.preventDefault();
  });

  // ДОБАВЛЕНО: Исправление ошибки с фокусом (aria-hidden) — добавлен setTimeout для правильного порядка событий
  let triggerElement = null;
  $('#reviewsModal').on('show.bs.modal', function(event) {
    triggerElement = event.relatedTarget;  // Автоматически передаётся Bootstrap
  });
  $('#reviewsModal').on('hide.bs.modal', function() {
    setTimeout(() => {
      if (triggerElement) {
        triggerElement.focus();  // Возвращаем фокус на кнопку открытия после применения aria-hidden
      }
    }, 0);
  });

  // ДОБАВЛЕНО: Обработчик закрытия модала — сброс всего, если не отправлено
  $('#reviewsModal').on('hidden.bs.modal', function() {
    if (!isSubmitting) {  // Только если форма не отправляется (чтобы не сбросить после отправки)
      resetAllPreviews();
    }
  });
});








// // Обработчик показать фото профиля в profile.html///////////////////////////////////////
// $(document).ready(function() {
//   // Функция показа уведомления посередине экрана
//   function showNotification(message, type = 'error', duration = 3000) {
//     $('.notification-alert').remove();
//     const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
//     const notification = $(`
//       <div class="notification-alert alert ${alertClass} text-center p-3 mb-0 shadow-lg" role="alert">
//         ${message}
//       </div>
//     `).css({
//       position: 'fixed',
//       top: '50%',
//       left: '50%',
//       transform: 'translate(-50%, -50%)',
//       zIndex: '9999',
//       maxWidth: '400px',
//       width: '90%',
//       opacity: '0',
//       transition: 'opacity 0.3s ease-in-out',
//       borderRadius: '8px'
//     });
//     $('body').append(notification);
//     notification.animate({ opacity: 1 }, 300);
//     setTimeout(function() {
//       notification.animate({ opacity: 0 }, 300, function() {
//         $(this).remove();
//       });
//     }, duration);
//   }

//   // Константы
//   const maxFileSize = 20 * 1024 * 1024; // 100 MB (синхронизировано с Nginx и сервером)
//   const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
//   const defaultImageSrc = $('#profileImage').data('default-src'); // Берем из data-default-src

//   // Функция проверки фото
//   function hasPhoto() {
//     const src = $('#profileImage').attr('src');
//     return src && src !== defaultImageSrc;
//   }

//   // Функция сброса превью
//   function resetPreview() {
//     $('#profileImage').animate({ opacity: 0 }, 200, function() {
//       $('#profileImage').attr('src', defaultImageSrc).attr('alt', 'Default User Photo');
//       $('#profileImage').animate({ opacity: 1 }, 300);
//     });
//     $('#photo-clear_id').val('true');
//     $('#id_photo').val('');
//     $('#photoButton').text('Добавить фото').prop('disabled', false);
//   }

//   // Обработчик кнопки
//   $('#photoButton').on('click', function() {
//     if (hasPhoto()) {
//       resetPreview();
//     } else {
//       $('#id_photo').click();
//     }
//   });

//   // Обработчик выбора файла
//   $('#id_photo').on('change', function(event) {
//     const file = event.target.files[0];
//     if (!file) return;

//     // Валидация типа
//     if (!allowedTypes.includes(file.type)) {
//       showNotification('Пожалуйста, выберите изображение в формате JPEG, PNG, GIF или WebP.');
//       resetPreview();
//       return;
//     }
//     // Валидация размера
//     if (file.size > maxFileSize) {
//       showNotification(`Размер файла не должен превышать ${maxFileSize / (1024 * 1024)} MB.`);
//       resetPreview();
//       return;
//     }

//     // Индикатор загрузки
//     $('#photoButton').text('Загрузка...').prop('disabled', true);

//     // Превью
//     const reader = new FileReader();
//     reader.onload = function(e) {
//       $('#profileImage').attr('src', e.target.result).attr('alt', 'User Photo').css('opacity', '0').animate({ opacity: 1 }, 300);
//       $('#photo-clear_id').val('false');
//       $('#photoButton').text('Удалить фото').prop('disabled', false);
//     };
//     reader.onerror = function() {
//       showNotification('Ошибка чтения файла. Попробуйте другой файл.');
//       resetPreview();
//     };
//     reader.readAsDataURL(file);
//   });

//   // Инициализация
//   if (!hasPhoto()) {
//     $('#photoButton').text('Добавить фото');
//   } else {
//     $('#photoButton').text('Удалить фото');
//   }
// });







// // Обработчик показать фото профиля в profile.html/////////////////////////////////////// новый
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
  const maxFileSize = 20 * 1024 * 1024; // 20 MB (исходный лимит перед компрессией, синхронизировано с Nginx и сервером)
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
    $('#photoButton').text('Компрессия...').prop('disabled', true);

    // Компрессия с помощью Compressor.js (качество 0.8, макс. размер 2MB)
    new Compressor(file, {
      quality: 0.8, // Качество (0.6-0.9 рекомендуется для баланса размера и качества)
      maxWidth: 1200, // Максимальная ширина (опционально, можно убрать если не нужно)
      maxHeight: 1200, // Максимальная высота (опционально)
      compress: true,
      success(result) {
        // Валидация после компрессии
        if (result.size > maxFileSize) {
          showNotification(`После компрессии размер файла всё ещё превышает ${maxFileSize / (1024 * 1024)} MB. Выберите меньшее изображение.`);
          resetPreview();
          return;
        }

        // Создание нового DataTransfer для замены файла в input
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(new File([result], file.name, { type: result.type }));

        // Замена файла в input (для отправки на сервер сжатой версии)
        event.target.files = dataTransfer.files;

        // Превью на основе сжатого файла
        const reader = new FileReader();
        reader.onload = function(e) {
          $('#profileImage').attr('src', e.target.result).attr('alt', 'User Photo').css('opacity', '0').animate({ opacity: 1 }, 300);
          $('#photo-clear_id').val('false');
          $('#photoButton').text('Удалить фото').prop('disabled', false);
          showNotification('Изображение сжато и загружено!', 'success'); // Опционально уведомление об успехе
        };
        reader.onerror = function() {
          showNotification('Ошибка чтения сжатого файла. Попробуйте другой файл.');
          resetPreview();
        };
        reader.readAsDataURL(result); // Используем result вместо file для превью
      },
      error(err) {
        console.error('Ошибка компрессии:', err);
        showNotification('Ошибка сжатия изображения. Попробуйте другой файл.');
        resetPreview();
      }
    });
  });

  // Инициализация
  if (!hasPhoto()) {
    $('#photoButton').text('Добавить фото');
  } else {
    $('#photoButton').text('Удалить фото');
  }
});


