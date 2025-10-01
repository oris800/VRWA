document.addEventListener('DOMContentLoaded', function() {
    
    const stockForm = document.getElementById('stockForm');
    if (stockForm) {
        const postUrl = stockForm.dataset.postUrl; 

        stockForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const cartButton = document.getElementById('cartButton');
            const responseMessage = document.getElementById('responseMessage');
            const formData = new URLSearchParams(new FormData(event.target));

            cartButton.disabled = true;
            cartButton.innerText = 'Checking...';
            responseMessage.innerHTML = '';

            try {
                const response = await fetch(postUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData
                });

                const responseText = await response.text();

                if (response.ok) {
                    if (responseText === 'in_stock') {
                        responseMessage.innerHTML = `<p style="color: green;">Item added to cart!</p>`;
                        cartButton.innerText = 'Added!';
                    } else if (responseText === 'out_of_stock') {
                        responseMessage.innerHTML = `<p style="color: red;">This item is out of stock.</p>`;
                        cartButton.innerText = 'Out of Stock';
                    } else {
                        responseMessage.innerHTML = `<p style="color: orange;">Response: ${responseText}</p>`;
                    }
                } else {
                    responseMessage.innerHTML = `<p style="color: red;">Error: ${responseText}</p>`;
                    cartButton.disabled = false;
                    cartButton.innerText = 'Try Again';
                }

            } catch (error) {
                console.error('Fetch Error:', error);
                responseMessage.innerHTML = '<p style="color: red;">A network error occurred.</p>';
                cartButton.disabled = false;
                cartButton.innerText = 'Try Again';
            }
        });
    }

    const pageWrapper = document.querySelector('.page-wrapper');
    if (pageWrapper) {
        const isAdmin = JSON.parse(pageWrapper.dataset.isAdmin || 'false');
        const deleteUrlBase = pageWrapper.dataset.deleteUrl;

        document.querySelector('.comments-list').addEventListener('click', function(event) {
            if (event.target && event.target.classList.contains('admin-delete-btn')) {
                if (!isAdmin) {
                    alert("Error: Insufficient privileges for this action.");
                    return;
                }
                const commentId = event.target.dataset.commentId;
                window.location.href = `${deleteUrlBase}?id=${commentId}`;
            }
        });
    }
});