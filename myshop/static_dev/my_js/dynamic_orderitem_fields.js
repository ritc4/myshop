(function($) {
    $(document).ready(function() {
        // Функция для toggling readonly на price на основе чекбокса
        function togglePriceEditable(row) {
            var checkbox = row.find('.field-is_price_custom input[type="checkbox"]');
            var priceInput = row.find('.field-price input');
            var isCustom = checkbox.is(':checked');

            if (isCustom) {
                priceInput.prop('readonly', false).removeClass('readonly-field');  // Делаем editable
                console.log('Price now editable (custom mode)');
            } else {
                priceInput.prop('readonly', true).addClass('readonly-field');  // Делаем readonly
                console.log('Price now readonly (auto mode)');
            }
        }

        // Инициализация для существующих строк
        $('.inline-related .field-is_price_custom input[type="checkbox"]').each(function() {
            var row = $(this).closest('tr');
            togglePriceEditable(row);
        });

        // Обработчик для чекбокса: toggle при change
        $(document).on('change', '.field-is_price_custom input[type="checkbox"]', function() {
            var row = $(this).closest('tr');
            togglePriceEditable(row);
        });

        // Автозаполнение price при выборе product_price (только если !is_price_custom)
        $(document).on('change', '.field-product_price select', function() {  // Для raw_id_fields (change сработает после выбора)
            var row = $(this).closest('tr');
            var productPriceId = $(this).val();
            var checkbox = row.find('.field-is_price_custom input[type="checkbox"]');
            var isCustom = checkbox.is(':checked');

            if (productPriceId && !isCustom) {  // Только если не custom
                var priceField = row.find('.field-price input');

                $.ajax({
                    url: '/orders/get-product-price-data/',  // URL из предыдущего решения (убедитесь, что он настроен)
                    data: { 'product_price_id': productPriceId },
                    success: function(data) {
                        if (data.error) {
                            alert('Ошибка: ' + data.error);
                        } else {
                            priceField.val(data.price);
                            console.log('Auto-filled price: ' + data.price + ' (non-custom mode)');
                            // Обновляем get_cost, если нужно (Django обновит при save)
                        }
                    },
                    error: function() {
                        alert('Ошибка при загрузке цены');
                    }
                });
            } else if (!productPriceId) {
                row.find('.field-price input').val('');  // Очистить, если product_price снят
            }
        });

        // Для динамически добавляемых строк (extra forms)
        $(document).on('formset:added', function(event, $row) {
            // Инициализировать toggle для новой строки
            setTimeout(function() {  // Небольшая задержка для рендера
                togglePriceEditable($row);
                $row.find('.field-product_price select').trigger('change');  // Автоинициализация
            }, 100);
        });
    });
})(django.jQuery);








