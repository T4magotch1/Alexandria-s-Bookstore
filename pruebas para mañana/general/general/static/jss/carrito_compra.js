document.addEventListener('DOMContentLoaded', () => {
  const cartItemsList = document.getElementById('cart-items-list');
  const savedItemsList = document.getElementById('saved-items-list');
  const noSavedItemsMsg = document.getElementById('no-saved-items');
  const savedCountSpan = document.getElementById('saved-count');
  const emptyCartDiv = document.getElementById('empty-cart');
  const cartIconBadge = document.getElementById('cart-item-count-badge'); // Get badge element

  // --- Event Delegation for Buttons ---
  cartItemsList.addEventListener('click', handleCartActions);
  savedItemsList.addEventListener('click', handleSavedItemsActions);

  // --- Initial Calculation ---
  // updateCartSummary(); // Call explicitly if initial HTML values might be wrong
  // updateSavedItemsUI(); // Call if there might be initial saved items
  // checkEmptyCart(); // Call to set initial empty state
  // updateCartIconBadge(); // Call to set initial badge count
  // NOTE: Since HTML is updated with correct initial values, these can be called implicitly
  // by the functions that modify the cart later. However, calling them ensures consistency.
  updateCartSummary();
  updateSavedItemsUI();
  checkEmptyCart();
  updateCartIconBadge();


  // --- Action Handlers ---
  function handleCartActions(event) {
    const target = event.target;
    const cartItem = target.closest('.cart-item');
    if (!cartItem) return;

    const quantityInput = cartItem.querySelector('.quantity-input');
    let quantity = parseInt(quantityInput.value, 10);

    if (target.closest('.increase-qty')) {
      quantityInput.value = quantity + 1;
      updateCartSummary();
    } else if (target.closest('.decrease-qty')) {
      if (quantity > 1) {
        quantityInput.value = quantity - 1;
        updateCartSummary();
      }
    } else if (target.closest('.remove-item')) {
      cartItem.remove();
      updateCartSummary();
      checkEmptyCart();
      // updateCartIconBadge(); // Called within checkEmptyCart
      // Optional: Add animation or confirmation
    } else if (target.closest('.save-item')) {
      saveItemForLater(cartItem);
      updateCartSummary();
      checkEmptyCart();
      // updateCartIconBadge(); // Called within checkEmptyCart
    }
  }

  function handleSavedItemsActions(event) {
      const target = event.target;
      const savedItem = target.closest('.saved-item');
      if (!savedItem) return;

      if (target.closest('.move-to-cart-btn')) {
          moveItemToCart(savedItem);
          // updateCartIconBadge(); // Called within checkEmptyCart after moving
      } else if (target.closest('.remove-saved-btn')) {
          savedItem.remove();
          updateSavedItemsUI();
          // Optional: Add animation or confirmation
      }
  }

  // --- Core Logic Functions ---
  function updateCartSummary() {
    let subtotal = 0;
    const items = cartItemsList.querySelectorAll('.cart-item');

    items.forEach(item => {
      const priceElement = item.querySelector('.cart-item-price');
      const quantityInput = item.querySelector('.quantity-input');
      const price = parseFloat(priceElement.textContent.replace('$', ''));
      const quantity = parseInt(quantityInput.value, 10);
      subtotal += price * quantity;
    });

    const taxRate = 0.08; // Example tax rate
    const tax = subtotal * taxRate;
    // Updated shipping logic example: Free over $50, $5 otherwise
    const shipping = subtotal >= 50 || subtotal === 0 ? 0 : 5.00;
    const total = subtotal + tax + shipping;

    document.getElementById('summary-subtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('summary-shipping').textContent = shipping === 0 ? 'FREE' : `$${shipping.toFixed(2)}`;
    document.getElementById('summary-tax').textContent = `$${tax.toFixed(2)}`;
    document.getElementById('summary-total').textContent = `$${total.toFixed(2)}`;
  }

  function saveItemForLater(cartItem) {
    // 1. Extract data from cart item
    const title = cartItem.querySelector('.cart-item-title').textContent.trim();
    const price = cartItem.querySelector('.cart-item-price').textContent.trim();
    const imgSrc = cartItem.querySelector('.cart-item-image').src;
    // Extract author/format if needed for saved item display
    // const details = cartItem.querySelector('.text-muted').textContent.trim();
    const itemId = cartItem.dataset.itemId || `saved-${Date.now()}`; // Use existing ID or generate one
    cartItem.dataset.itemId = itemId; // Ensure item has an ID before saving

    // 2. Create saved item HTML
    const savedItemHTML = `
      <div class="saved-item" data-item-id="${itemId}">
        <img src="${imgSrc}" alt="${title}">
        <div class="saved-item-details">
          <div class="saved-item-title">${title}</div>
          <!-- Optional: Add details back if needed: <small class="text-muted d-block">${details}</small> -->
          <div class="saved-item-price">${price}</div>
        </div>
        <div class="saved-item-actions d-flex flex-column flex-sm-row gap-1">
          <button class="btn btn-sm btn-outline-success move-to-cart-btn">
            <i class="fas fa-shopping-cart me-1"></i> Move to Cart
          </button>
          <button class="btn btn-sm btn-outline-danger remove-saved-btn">
            <i class="fas fa-trash-alt"></i>
          </button>
        </div>
      </div>
    `;

    // 3. Append to saved items list
    savedItemsList.insertAdjacentHTML('beforeend', savedItemHTML);

    // 4. Remove from cart
    cartItem.remove();

    // 5. Update UI
    updateSavedItemsUI();
    // updateCartSummary() and checkEmptyCart() called by caller
  }

  function moveItemToCart(savedItem) {
      // 1. Extract data
      const title = savedItem.querySelector('.saved-item-title').textContent.trim();
      const price = savedItem.querySelector('.saved-item-price').textContent.trim();
      const imgSrc = savedItem.querySelector('img').src;
      const itemId = savedItem.dataset.itemId;
      // Extract details if they were stored and needed
      // const details = savedItem.querySelector('.text-muted') ? savedItem.querySelector('.text-muted').textContent.trim() : '';

      // 2. Create cart item HTML
      const cartItemHTML = `
          <div class="card cart-item mb-3 shadow-sm" data-item-id="${itemId}">
              <div class="row g-0">
                  <div class="col-md-3 d-flex align-items-center justify-content-center p-2">
                      <img src="${imgSrc}" class="img-fluid rounded cart-item-image" alt="${title}">
                  </div>
                  <div class="col-md-9">
                      <div class="card-body d-flex flex-column h-100">
                          <h5 class="card-title cart-item-title mb-1">${title}</h5>
                          <!-- Recreate details - might need more robust data storage -->
                          <small class="text-muted mb-2">Details may vary</small>
                          <div class="cart-item-price fw-bold text-success mb-3">${price}</div>
                          <div class="d-flex align-items-center mb-3">
                              <label for="quantity-${itemId}" class="form-label me-2 mb-0">Qty:</label>
                              <div class="input-group quantity-selector" style="max-width: 120px;">
                                  <button class="btn btn-outline-secondary quantity-btn decrease-qty" type="button"><i class="fas fa-minus"></i></button>
                                  <input type="number" class="form-control text-center quantity-input" value="1" min="1" id="quantity-${itemId}" aria-label="Item quantity">
                                  <button class="btn btn-outline-secondary quantity-btn increase-qty" type="button"><i class="fas fa-plus"></i></button>
                              </div>
                          </div>
                          <div class="cart-item-actions mt-auto d-flex gap-2">
                              <button class="btn btn-sm btn-outline-primary save-item"><i class="far fa-heart me-1"></i> Save for Later</button>
                              <button class="btn btn-sm btn-outline-danger remove-item"><i class="fas fa-trash-alt me-1"></i> Remove</button>
                          </div>
                      </div>
                  </div>
              </div>
          </div>
      `;

      // 3. Append to cart items list
      cartItemsList.insertAdjacentHTML('beforeend', cartItemHTML);

      // 4. Remove from saved items
      savedItem.remove();

      // 5. Update UI
      updateCartSummary();
      updateSavedItemsUI();
      checkEmptyCart();
      // updateCartIconBadge() called within checkEmptyCart
  }


  function updateSavedItemsUI() {
    const savedItems = savedItemsList.querySelectorAll('.saved-item');
    const count = savedItems.length;
    savedCountSpan.textContent = count;

    if (count === 0) {
      noSavedItemsMsg.style.display = 'block';
    } else {
      noSavedItemsMsg.style.display = 'none';
    }
  }

  function checkEmptyCart() {
      const items = cartItemsList.querySelectorAll('.cart-item');
      if (items.length === 0) {
          emptyCartDiv.classList.remove('d-none');
      } else {
          emptyCartDiv.classList.add('d-none');
      }
      // Update badge whenever empty state changes
      updateCartIconBadge();
  }

  // --- Update Cart Icon Badge ---
  function updateCartIconBadge() {
      const itemCount = cartItemsList.querySelectorAll('.cart-item').length;
      if (cartIconBadge) {
          cartIconBadge.textContent = itemCount;
          if (itemCount === 0) {
              cartIconBadge.classList.add('hidden-badge');
          } else {
              cartIconBadge.classList.remove('hidden-badge');
          }
      }
  }

  // --- Input Change Listener ---
  cartItemsList.addEventListener('change', (event) => {
      if (event.target.classList.contains('quantity-input')) {
          if (parseInt(event.target.value, 10) < 1 || isNaN(parseInt(event.target.value, 10))) {
              event.target.value = 1;
          }
          updateCartSummary();
      }
  });

});
