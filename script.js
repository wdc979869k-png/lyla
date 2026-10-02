let cart = [];

function addToCart(name, price) {
    cart.push({
        name: name,
        price: price
    });

    updateCart();

    alert(name + " was added to your cart!");
}

function removeFromCart(index) {
    cart.splice(index, 1);
    updateCart();
}

function updateCart() {
    const cartItems = document.getElementById("cart-items");
    const cartCount = document.getElementById("cart-count");
    const totalElement = document.getElementById("total");

    cartItems.innerHTML = "";

    let total = 0;

    cart.forEach((item, index) => {
        total += item.price;

        const div = document.createElement("div");

        div.className = "cart-item";

        div.innerHTML = `
            <span>${item.name} - $${item.price}</span>
            <button class="remove" onclick="removeFromCart(${index})">
                Remove
            </button>
        `;

        cartItems.appendChild(div);
    });

    cartCount.textContent = cart.length;
    totalElement.textContent = total;
}

function showCart() {
    document.getElementById("cart").style.display = "flex";
}

function closeCart() {
    document.getElementById("cart").style.display = "none";
}

function checkout() {
    if (cart.length === 0) {
        alert("Your cart is empty!");
        return;
    }

    alert("Thank you for your purchase! 🎉");

    cart = [];
    updateCart();
    closeCart();
}
```
