document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const firstName = event.target.firstName.value;
    const lastName = event.target.lastName.value;
    const email = event.target.email.value;
    const passwd = event.target.password.value;
    const fbAccessToken = event.target.fbAccessToken.value;
    const errorMessageElement = document.getElementById('error-message');

        const response = await fetch('http://localhost:5555/register-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'email': email,
                'passwd': passwd,
                'first_name': firstName,
                'last_name': lastName,
                'fb_access_token': fbAccessToken,
                'admin': false
            })
        });

        const data = await response.json();
        if (data.status == 200){
            alert('User registered');
            window.location.href = 'http://localhost:5000/login';
        } else if (data.error) {
            message = data.error.message;
            alert(message);
        } else {
            alert('Unexpected error');
        } 
});
    