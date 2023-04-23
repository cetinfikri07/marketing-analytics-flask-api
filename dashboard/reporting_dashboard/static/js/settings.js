$(document).ready(function(){
    const token = localStorage.getItem('token');
    const firstName = localStorage.getItem('first_name');
    const lastName = localStorage.getItem('last_name');
    if (!token) {
        // Redirect the user to the login page
        window.location.href = 'http://localhost:5000/login';
        return;
    };

    const today = new Date();
    const oneWeekAgo = new Date();
    oneWeekAgo.setTime(today.getTime() - (7 * 24 * 60 * 60 * 1000));

    $('.text-dark').text(firstName + ' ' + lastName);

    $(function () {
        $('input[name="daterange"]').daterangepicker({
            opens: 'left',
            startDate: oneWeekAgo,
            endDate: today,
            showDropdowns: false,
            locale: {
                format: 'YYYY-MM-DD'
            }
        })
    });

    $('#registerBtn').click(async function(event){
        event.preventDefault();
        var accountId = $('#fbAccountId').val();
        var dateStart = $('input[name="daterange"]').val().split(' - ')[0];
        var dateStop = $('input[name="daterange"]').val().split(' - ')[1];

        try {
            $('section.loading').show();
            const response = await fetch('http://127.0.0.1:5555/meta/register',{
                method:'POST',
                headers: {
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({'facebook_account_id':accountId,"since":dateStart,"until":dateStop})
            });

            const result = await response.json();
            $('section.loading').hide();

            console.log(result);

        } catch (error){
            console.log('Error: ', error);
        };


    
    });

});




