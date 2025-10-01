document.addEventListener('DOMContentLoaded', function() {
    
    // --- לוגיקה עבור טופס בדיקת המלאי (SSRF) ---
    const stockForm = document.getElementById('stockForm');
    if (stockForm) {
        const postUrl = stockForm.dataset.postUrl; // קריאת ה-URL מה-data attribute

        stockForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const cartButton = document.getElementById('cartButton');
            const responseMessage = document.getElementById('responseMessage');
            // חשוב: זה החלק שאוסף את פרמטר ה-stockapi מהטופס, מה שמאפשר את ה-SSRF
            const formData = new URLSearchParams(new FormData(event.target));

            cartButton.disabled = true;
            cartButton.innerText = 'Checking...';
            responseMessage.innerHTML = '';

            try {
                // שימוש במשתנה postUrl שקראנו מה-HTML
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
                        // זה המקום שבו תראה את התגובה מה-SSRF שלך!
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

    // --- לוגיקה עבור מחיקת תגובות על ידי אדמין ---
    const pageWrapper = document.querySelector('.page-wrapper');
    if (pageWrapper) {
        // קריאת הנתונים מה-div הראשי
        const isAdmin = JSON.parse(pageWrapper.dataset.isAdmin || 'false');
        const deleteUrlBase = pageWrapper.dataset.deleteUrl;

        // שימוש ב-Event Delegation כדי לטפל בכל כפתורי המחיקה
        document.querySelector('.comments-list').addEventListener('click', function(event) {
            // בדוק אם האלמנט שנלחץ הוא כפתור מחיקה של אדמין
            if (event.target && event.target.classList.contains('admin-delete-btn')) {
                if (!isAdmin) {
                    alert("Error: Insufficient privileges for this action.");
                    return;
                }
                const commentId = event.target.dataset.commentId;
                // בנה את ה-URL הסופי והפנה את המשתמש
                window.location.href = `${deleteUrlBase}?id=${commentId}`;
            }
        });
    }
});