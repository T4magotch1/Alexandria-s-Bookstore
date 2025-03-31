document.addEventListener('DOMContentLoaded', function() {
    // Cart functionality
    let cartCount = 0;
    const cartCounter = document.getElementById('cart-counter');
    const addToCartBtn = document.getElementById('add-to-cart-btn');
    const quantityInput = document.getElementById('inputQuantity');
    
    // Check if there's existing cart data in localStorage
    if (localStorage.getItem('cartCount')) {
        cartCount = parseInt(localStorage.getItem('cartCount'));
        cartCounter.textContent = cartCount;
    }
    
    // Add to cart button click handler
    addToCartBtn.addEventListener('click', function() {
        const quantity = parseInt(quantityInput.value);
        const maxQuantity = 5; // Based on the max attribute in the input
        
        if (quantity > maxQuantity) {
            alert(`You can only add up to ${maxQuantity} items of this book.`);
            return;
        }
        
        cartCount += quantity;
        cartCounter.textContent = cartCount;
        
        // Save to localStorage
        localStorage.setItem('cartCount', cartCount);
        
        // Show success message
        const originalText = addToCartBtn.innerHTML;
        addToCartBtn.innerHTML = '<i class="bi-check-circle-fill me-1"></i> Added to cart';
        addToCartBtn.classList.add('btn-success');
        addToCartBtn.classList.remove('btn-outline-dark');
        
        // Reset button after 2 seconds
        setTimeout(() => {
            addToCartBtn.innerHTML = originalText;
            addToCartBtn.classList.remove('btn-success');
            addToCartBtn.classList.add('btn-outline-dark');
        }, 2000);
        
        // Here you would typically also add the item details to the cart
        // For a complete implementation, you'd want to store the cart items in localStorage
    });
    
    // Quantity input validation
    quantityInput.addEventListener('change', function() {
        const value = parseInt(this.value);
        const max = parseInt(this.max);
        const min = parseInt(this.min);
        
        if (isNaN(value) || value < min) {
            this.value = min;
        } else if (value > max) {
            this.value = max;
        }
    });
    
    // In a real application, you would fetch the book details from an API or database
    // For this example, we're just using the static data from the HTML
    
    // Related books functionality would go here
    // You would typically fetch related books based on category/genre
});