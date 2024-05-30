$(document).ready(function() {
    let userId = 1; // Replace with actual user ID from Telegram Bot

    $('#clicker-button').click(function() {
        $.post('/click', { telegram_id: userId }, function(data) {
            $('#balance').text(data.balance);
        });
    });

    function fetchPrice() {
        $.get('/btc-price', function(data) {
            $('#price').text(data.price);
        });
    }

    $('#trade-button').click(function() {
        let amount = $('#amount').val();
        let price = $('#price').text();
        $.post('/trade', { user_id: userId, amount: amount, price: price }, function(data) {
            alert(data.message);
        });
    });

    setInterval(fetchPrice, 5000);
    fetchPrice();
});
