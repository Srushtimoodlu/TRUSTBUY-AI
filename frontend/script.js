
const API_URL = "http://127.0.0.1:5000";

const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const productList = document.getElementById("productList");
const resultMessage = document.getElementById("resultMessage");

const budgetInput = document.getElementById("budgetInput");
const budgetButton = document.getElementById("budgetButton");
const clearButton = document.getElementById("clearButton");

const comparisonContent = document.getElementById("comparisonContent");
const cartContent = document.getElementById("cartContent");
const cartCount = document.getElementById("cartCount");

let products = [];
let filteredProducts = [];
let comparedProducts = [];
let cart = [];

function makeElement(tag, className, value) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (value !== undefined) el.textContent = String(value);
    return el;
}

function productEmoji(product) {
    const category = String(product.category || "").toLowerCase();
    const name = String(product.name || "").toLowerCase();

    if (category.includes("mobile") || name.includes("galaxy") ||
        name.includes("phone") || name.includes("iphone")) return "📱";

    if (category.includes("laptop") || name.includes("laptop")) return "💻";
    if (category.includes("audio") || name.includes("headphone")) return "🎧";
    if (category.includes("watch") || name.includes("watch")) return "⌚";
    if (category.includes("camera")) return "📷";
    if (category.includes("tv")) return "📺";

    return "🛍️";
}

function addInfo(container, label, value) {
    container.appendChild(
        makeElement("p", "", `${label}: ${value}`)
    );
}

// SEARCH

async function searchProducts() {
    const keyword = searchInput.value.trim();

    if (!keyword) {
        resultMessage.textContent = "Please enter a product name.";
        return;
    }

    searchButton.disabled = true;
    productList.replaceChildren();
    resultMessage.textContent = "Finding products...";

    try {
        const response = await fetch(
            `${API_URL}/search?keyword=${encodeURIComponent(keyword)}`
        );

        if (!response.ok) throw new Error("Search failed.");

        const data = await response.json();

        if (!Array.isArray(data)) {
            throw new Error("Invalid product response.");
        }

        products = data;
        filteredProducts = [...products];
        comparedProducts = [];

        renderComparison();
        renderProducts();

    } catch (error) {
        resultMessage.textContent =
            "Unable to connect to backend. Check whether Flask is running.";
        console.error(error);
    } finally {
        searchButton.disabled = false;
    }
}

// DISPLAY PRODUCTS

function renderProducts() {
    productList.replaceChildren();

    if (filteredProducts.length === 0) {
        resultMessage.textContent = "No products found.";
        return;
    }

    resultMessage.textContent =
        `${filteredProducts.length} products found.`;

    filteredProducts.forEach(product => {
        const card = makeElement("article", "product-card");

        card.appendChild(
            makeElement("div", "product-image", productEmoji(product))
        );

        card.appendChild(
            makeElement("h3", "", product.name || "Product")
        );

        addInfo(card, "Product ID", product.id ?? "N/A");
        addInfo(card, "Brand", product.brand ?? "N/A");

        card.appendChild(
            makeElement(
                "p",
                "product-price",
                `₹${product.price ?? "N/A"}`
            )
        );

        addInfo(card, "Rating", `${product.rating ?? "N/A"} / 5`);

        const stock = Number(product.stock) > 0;

        card.appendChild(
            makeElement(
                "p",
                stock ? "stock-good" : "stock-bad",
                stock ? "✓ In Stock" : "✕ Out of Stock"
            )
        );

        const actions = makeElement("div", "product-actions");

        const compareButton = makeElement(
            "button",
            "light-button",
            comparedProducts.some(p => p.id === product.id)
                ? "Selected ✓"
                : "Compare"
        );

        compareButton.addEventListener("click", () => {
            toggleCompare(product);
        });

        actions.appendChild(compareButton);

        const cartButton = makeElement(
            "button",
            "",
            "Add to Cart"
        );

        cartButton.disabled = !stock;

        cartButton.addEventListener("click", () => {
            addToCart(product);
        });

        actions.appendChild(cartButton);
        card.appendChild(actions);

        const trustButton = makeElement(
            "button",
            "trust-button",
            "🛡 Check Trust Score"
        );

        trustButton.addEventListener("click", () => {
            checkTrustScore(product, card, trustButton);
        });

        card.appendChild(trustButton);

        productList.appendChild(card);
    });
}

// TRUST SCORE

async function checkTrustScore(product, card, button) {
    button.disabled = true;
    button.textContent = "Checking...";

    try {
        const response = await fetch(
            `${API_URL}/trust-score?product_id=${encodeURIComponent(product.id)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.message || "Trust score unavailable");
        }

        const score = Number(data.trust_score);

        if (!Number.isFinite(score) || score < 0 || score > 100) {
            throw new Error("Invalid trust score returned by backend.");
        }

        const result = makeElement(
            "div",
            "trust-result",
            `🛡 Trust Score: ${score}/100`
        );

        const oldResult = card.querySelector(".trust-result");
        if (oldResult) oldResult.remove();

        card.appendChild(result);

        button.textContent = "✓ Trust Score Checked";

    } catch (error) {
        alert(error.message);
        button.textContent = "🛡 Check Trust Score";
        console.error(error);
    } finally {
        button.disabled = false;
    }
}

// BUDGET FILTER

budgetButton.addEventListener("click", () => {
    const value = budgetInput.value;

    if (value.trim() === "" || !Number.isFinite(Number(value)) ||
        Number(value) < 0) {
        resultMessage.textContent = "Enter a valid budget.";
        return;
    }

    const budget = Number(value);

    filteredProducts = products.filter(product => {
        return Number.isFinite(Number(product.price)) &&
            Number(product.price) <= budget;
    });

    renderProducts();
});

clearButton.addEventListener("click", () => {
    budgetInput.value = "";
    filteredProducts = [...products];
    renderProducts();
});

// COMPARISON

function toggleCompare(product) {
    const exists = comparedProducts.some(p => p.id === product.id);

    if (exists) {
        comparedProducts = comparedProducts.filter(
            p => p.id !== product.id
        );
    } else {
        if (comparedProducts.length >= 3) {
            alert("You can compare up to 3 products.");
            return;
        }

        comparedProducts.push(product);
    }

    renderProducts();
    renderComparison();
}

function renderComparison() {
    comparisonContent.replaceChildren();

    if (comparedProducts.length === 0) {
        comparisonContent.textContent =
            "Select products to compare.";
        return;
    }

    const table = document.createElement("table");
    const header = document.createElement("tr");

    header.appendChild(makeElement("th", "", "Feature"));

    comparedProducts.forEach(product => {
        header.appendChild(
            makeElement("th", "", product.name)
        );
    });

    table.appendChild(header);

    const fields = [
        ["Brand", "brand"],
        ["Price", "price"],
        ["Rating", "rating"],
        ["Stock", "stock"]
    ];

    fields.forEach(([label, key]) => {
        const row = document.createElement("tr");
        row.appendChild(makeElement("td", "", label));

        comparedProducts.forEach(product => {
            let value = product[key] ?? "N/A";

            if (key === "price") value = `₹${value}`;

            if (key === "stock") {
                value = Number(value) > 0
                    ? "Available"
                    : "Out of stock";
            }

            row.appendChild(makeElement("td", "", value));
        });

        table.appendChild(row);
    });

    comparisonContent.appendChild(table);

    const clear = makeElement(
        "button",
        "light-button",
        "Clear Comparison"
    );

    clear.style.marginTop = "15px";

    clear.addEventListener("click", () => {
        comparedProducts = [];
        renderProducts();
        renderComparison();
    });

    comparisonContent.appendChild(clear);
}

// CART

function addToCart(product) {
    if (Number(product.stock) <= 0) {
        alert("Product is out of stock.");
        return;
    }

    const existing = cart.find(p => p.id === product.id);

    if (existing) {
        if (existing.quantity >= Number(product.stock)) {
            alert("Maximum available stock reached.");
            return;
        }

        existing.quantity++;
    } else {
        cart.push({...product, quantity: 1});
    }

    renderCart();
    alert("Product added to cart!");
}

function removeFromCart(id) {
    cart = cart.filter(p => p.id !== id);
    renderCart();
}

function renderCart() {
    cartContent.replaceChildren();

    const count = cart.reduce(
        (total, item) => total + item.quantity, 0
    );

    cartCount.textContent = count;

    if (cart.length === 0) {
        cartContent.textContent = "Your cart is empty.";
        return;
    }

    let total = 0;

    cart.forEach(product => {
        const price = Number(product.price) || 0;
        total += price * product.quantity;

        const item = makeElement("div", "cart-item");
        const details = document.createElement("div");

        details.appendChild(
            makeElement("strong", "", product.name)
        );

        addInfo(details, "Price", `₹${price}`);
        addInfo(details, "Quantity", product.quantity);

        const remove = makeElement(
            "button",
            "remove-button",
            "Remove"
        );

        remove.addEventListener("click", () => {
            removeFromCart(product.id);
        });

        item.appendChild(details);
        item.appendChild(remove);
        cartContent.appendChild(item);
    });

    cartContent.appendChild(
        makeElement(
            "p",
            "cart-total",
            `Total: ₹${total.toFixed(2)}`
        )
    );

    cartContent.appendChild(
        makeElement(
            "p",
            "",
            "Demo cart only. No actual payment is processed."
        )
    );
}

// EVENTS

searchButton.addEventListener("click", searchProducts);

searchInput.addEventListener("keydown", event => {
    if (event.key === "Enter") searchProducts();
});

renderComparison();
renderCart();

const aiButton = document.getElementById("aiButton");

aiButton.addEventListener("click", async () => {
    const query = document.getElementById("aiQuery").value.trim();
    const result = document.getElementById("aiResult");

    if (!query) {
        result.textContent = "Please enter your shopping requirements.";
        return;
    }

    aiButton.disabled = true;
    aiButton.textContent = "Thinking...";

    try {
        const response = await fetch(`${API_URL}/recommend`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "AI recommendation failed.");
        }

        result.textContent = JSON.stringify(data, null, 2);

    } catch (error) {
        result.textContent = error.message;
    } finally {
        aiButton.disabled = false;
        aiButton.textContent = "Get AI Recommendations →";
    }
});
