document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const email = event.target.email.value;
    const passwd = event.target.password.value;
    const errorMessageElement = document.getElementById('error-message');

    try {
        const response = await fetch('http://localhost:5555/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, passwd })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        };

        const data = await response.json();

        if (data.token) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('first_name',data.first_name);
            localStorage.setItem('last_name',data.last_name);
            window.location.href = 'http://localhost:5000/';
        } else {
            errorMessageElement.innerText = 'Invalid username or password';
        }
    } catch (error) {
        console.error('Error:', error);
        errorMessageElement.innerText = 'Invalid username or password';
    }
});
    