// המתן עד שכל תוכן העמוד ייטען לפני הרצת הסקריפט
document.addEventListener('DOMContentLoaded', function() {

    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        const loginUrl = loginForm.dataset.loginUrl;
        const checkUserUrl = loginForm.dataset.checkUrl;

        loginForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const errorContainer = document.getElementById('errorMessageContainer');
            errorContainer.innerHTML = '';

            const urlEncodedData = new URLSearchParams(new FormData(event.target));

            try {
                const loginResponse = await fetch(loginUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: urlEncodedData,
                });

                if (loginResponse.ok) {
                    const userId = loginResponse.headers.get('X-User-ID');
                    const redirectUrl = loginResponse.headers.get('X-Redirect-Url');

                    const hiddenUrlEncodedData = new URLSearchParams();
                    hiddenUrlEncodedData.append('id', userId);


                    await fetch(checkUserUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: hiddenUrlEncodedData
                    });
                    
                    window.location.href = redirectUrl;

                } else {
                    const errorMessage = await loginResponse.text();
                    errorContainer.innerHTML = `<div class="message message-error">${errorMessage}</div>`;
                }

            } catch (error) {
                console.error('An error occurred:', error);
                errorContainer.innerHTML = `<div class="message message-error">An unexpected error occurred.</div>`;
            }
        });
    }
});