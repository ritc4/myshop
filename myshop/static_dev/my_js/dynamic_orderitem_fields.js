// (function($) {
//     $(document).ready(function() {
//         console.log("JS loaded and ready");

//         // Функция для инициализации строки (очистка и загрузка размеров)
//         function initializeRow(row) {
//             console.log("Initializing row:", row.index());

//             const productInput = row.find('.field-product input.vForeignKeyRawIdAdminField');
//             const sizeSelect = row.find('.field-size select');

//             const productId = productInput.val();
//             const currentSizeId = sizeSelect.val();  // Сохраняем текущий выбранный размер
//             console.log("Product ID:", productId, "Current Size ID:", currentSizeId);

//             if (!productId) {
//                 sizeSelect.empty().append('<option value="">---------</option>');
//                 return;
//             }

//             // Очистить и загрузить размеры
//             sizeSelect.empty().append('<option value="">---------</option>');
//             $.ajax({
//                 url: '/rws!-cozy-admin/orders/order/get_sizes/' + productId + '/',
//                 method: 'GET',
//                 success: function(data) {
//                     if (data.sizes && data.sizes.length > 0) {
//                         data.sizes.forEach(function(size) {
//                             sizeSelect.append('<option value="' + size.id + '">' + size.title + '</option>');
//                         });
//                         // Восстановить выбор, если текущий размер доступен
//                         if (currentSizeId && sizeSelect.find('option[value="' + currentSizeId + '"]').length > 0) {
//                             sizeSelect.val(currentSizeId);
//                         }
//                         console.log("Sizes loaded for product", productId, data.sizes, "Restored size:", sizeSelect.val());
//                     } else {
//                         console.log("No sizes found for product", productId);
//                     }
//                 },
//                 error: function(xhr) {
//                     console.error("Error loading sizes:", xhr.status, xhr.responseText);
//                     // Можно добавить уведомление: alert('Ошибка загрузки размеров.');
//                 }
//             });
//         }

//         // Функция для обновления цен (без изменений)
//         function updatePrice(row) {
//             const productInput = row.find('.field-product input.vForeignKeyRawIdAdminField');
//             const sizeSelect = row.find('.field-size select');
//             const priceInput = row.find('.field-price input');
//             const zakupPriceP = row.find('.field-product_zacup_price p');

//             const productId = productInput.val();
//             const sizeId = sizeSelect.val();

//             if (!productId || !sizeId) return;

//             $.ajax({
//                 url: '/rws!-cozy-admin/orders/order/get_prices/' + productId + '/' + sizeId + '/',
//                 method: 'GET',
//                 success: function(data) {
//                     if (data.price) priceInput.val(data.price);
//                     if (data.zacup_price) zakupPriceP.text(data.zacup_price);
//                     console.log("Prices updated", data);
//                 },
//                 error: function(xhr) {
//                     console.error("Error loading prices:", xhr.status, xhr.responseText);
//                     // Можно добавить: alert('Цена не найдена для выбранного размера.');
//                 }
//             });
//         }

//         // Инициализировать ВСЕ существующие строки (не только dynamic-items, исключая add-row)
//         $('#items-group tbody tr').not('.add-row').each(function() {
//             initializeRow($(this));
//         });

//         // Обработчик изменения продукта
//         $('#items-group').on('input change blur', '.field-product input.vForeignKeyRawIdAdminField', function() {
//             const row = $(this).closest('tr');
//             initializeRow(row);
//         });

//         // Обработчик изменения размера
//         $('#items-group').on('change', '.field-size select', function() {
//             const row = $(this).closest('tr');
//             updatePrice(row);
//         });

//         // Инициализация для НОВЫХ строк (formset:added)
//         $(document).on('formset:added', '#items-group tbody tr', function(event, $row) {
//             initializeRow($row);
//         });
//     });
// })(django.jQuery);





// static/admin/js/dynamic_orderitem.js
// (function($) {
//     $(document).ready(function() {
//         // Функция для обновления полей при выборе продукта (только опции размера и readonly поля)
//         function updateFields(row) {
//             const productInput = $(row).find('input[name$="-product"]');
//             const productId = productInput.val().trim();
//             if (!productId) {
//                 clearFields(row);
//                 return;
//             }

//             // AJAX-запрос к API (исправлен URL: /api/products/ вместо /api/product/)
//             fetch(`/api/product/${productId}/`, {
//                 method: 'GET',
//                 headers: {
//                     'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
//                     'Content-Type': 'application/json',
//                 },
//             })
//             .then(response => {
//                 if (!response.ok) {
//                     throw new Error(`HTTP ${response.status}`);
//                 }
//                 return response.json();
//             })
//             .then(data => {
//                 if (data.error) {
//                     alert(`Ошибка: ${data.error}`);
//                     clearFields(row);
//                     return;
//                 }

//                 // Обновить readonly поля
//                 $(row).find('.field-product_article_number p').text(data.article_number || 'Артикул не указан');
//                 $(row).find('.field-product_mesto p').text(data.mesto || 'Место не указано');
//                 const imgTag = (data.images && data.images.length > 0) ? `<img src="${data.images[0].image}" width="50" alt="Фото">` : 'Нет фото';
//                 $(row).find('.field-product_image div').html(imgTag);

//                 // Обновить size select (загрузить опции, но не трогать цену)
//                 const sizeSelect = $(row).find('select[name$="-size"]');
//                 const currentSizeValue = sizeSelect.val();  // Сохранить текущий выбранный размер (для существующих строк)
//                 sizeSelect.empty().append('<option value="">---------</option>');
//                 if (data.sizes_and_prices) {
//                     data.sizes_and_prices.forEach(pp => {
//                         sizeSelect.append(`<option value="${pp.size_id}">${pp.size}</option>`);
//                     });
//                 }

//                 $(row).data('sizes_and_prices', data.sizes_and_prices || []);

//                 // Для существующих строк: установить selected на сохранённый размер, если он есть в опциях
//                 let selectedSizeId = '';
//                 if (currentSizeValue && data.sizes_and_prices.some(pp => pp.size_id == currentSizeValue)) {
//                     sizeSelect.val(currentSizeValue);
//                     selectedSizeId = currentSizeValue;
//                 } else {
//                     // Если сохранённый размер не в опциях, сбросить (для новых или изменённых продуктов)
//                     sizeSelect.val('');
//                 }

//                 // Новое: Для инициализации — обновить только закупочную цену, если размер выбран (без трогания розничной цены)
//                 if (selectedSizeId) {
//                     updateZacupPriceOnly(row, selectedSizeId);
//                 }

//                 // Не вызываем updatePriceOnSizeChange здесь, чтобы не перезаписывать существующую розничную цену
//             })
//             .catch(error => {
//                 console.error('Ошибка AJAX:', error);
//                 alert('Не удалось загрузить данные продукта');
//                 clearFields(row);
//             });
//         }

//         // Новая функция: Обновление только закупочной цены (для init, без изменения input[name$="-price"])
//         function updateZacupPriceOnly(row, selectedSizeId) {
//             const sizesAndPrices = $(row).data('sizes_and_prices') || [];
//             const selectedPp = sizesAndPrices.find(pp => pp.size_id == selectedSizeId);
//             const zacupPriceField = $(row).find('.field-product_zacup_price p');

//             if (selectedPp && selectedPp.zacup_price) {
//                 zacupPriceField.text(selectedPp.zacup_price);
//             } else {
//                 zacupPriceField.text('Не указано');
//             }
//         }

//         // Функция для обновления цен при выборе размера (для change события — обновляет розничную цену)
//         function updatePriceOnSizeChange(row) {
//             const sizesAndPrices = $(row).data('sizes_and_prices') || [];
//             const sizeSelect = $(row).find('select[name$="-size"]');
//             const selectedSizeId = sizeSelect.val();
//             const priceInput = $(row).find('input[name$="-price"]');
//             const zacupPriceField = $(row).find('.field-product_zacup_price p');

//             if (!selectedSizeId) {
//                 // Не очищаем цену, оставляем как есть (для существующих строк)
//                 zacupPriceField.text('');
//                 return;
//             }

//             const selectedPp = sizesAndPrices.find(pp => pp.size_id == selectedSizeId);
//             if (selectedPp) {
//                 // Обновляем розничную цену при выборе размера
//                 priceInput.val(selectedPp.price || '');
//                 zacupPriceField.text(selectedPp.zacup_price || '');
//             } else {
//                 // Не очищаем, если размер не найден
//                 zacupPriceField.text('');
//             }
//         }

//         // Функция очистки (очищает size и price при пустом продукте; удаляет все опции size)
//         function clearFields(row) {
//             $(row).find('.field-product_article_number p').text('Артикул не указан');
//             $(row).find('.field-product_mesto p').text('Место не указано');
//             $(row).find('.field-product_image div').html('Нет фото');
//             const sizeSelect = $(row).find('select[name$="-size"]');
//             sizeSelect.empty().append('<option value="">---------</option>');
//             sizeSelect.val('');  // Явно сбросить val для надёжности
//             const priceInput = $(row).find('input[name$="-price"]');
//             priceInput.val('');  // Очистить розничную цену при пустом продукте
//             $(row).find('.field-product_zacup_price p').text('');
//             $(row).data('sizes_and_prices', []);
//         }

//         // Слушатели (динамические изменения)
//         $(document).on('change', 'input[name$="-product"]', function() {
//             const row = $(this).closest('tr');
//             updateFields(row);  // Автоматически очистит, если product стал пустым
//         });

//         $(document).on('change', 'select[name$="-size"]', function() {
//             const row = $(this).closest('tr');
//             updatePriceOnSizeChange(row);
//         });

//         // Инициализация при загрузке формы (усиленная: для ВСЕХ строк)
//         $('input[name$="-product"]').each(function() {
//             const row = $(this).closest('tr');
//             const productId = $(this).val().trim();
//             if (productId) {
//                 // Товар добавлен: загрузить динамические опции size и поля
//                 updateFields(row);
//             } else {
//                 // Товар не добавлен: явно очистить size до пустого состояния
//                 clearFields(row);
//             }
//         });
//     });
// })(django.jQuery);
