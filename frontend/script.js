
const API_URL = "http://127.0.0.1:5000";

const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const productList = document.getElementById("productList");
const resultMessage = document.getElementById("resultMessage");

let allProducts = [];
let comparisonProducts = [];
let cart = [];

// BASIC HELPERS

function makeElement(tag, className = "", content = "") {
    const element = document.createElement(tag);
    element.className = className;
    element.textContent = content;
    return element;
}

function productEmoji(product) {
    const name = (product.name || "").toLowerCase();

    if (name.includes("phone") || name.includes("galaxy") ||
        name.includes("iphone")) return "📱";

    if (name.includes("laptop")) return "💻";
    if (name.includes("headphone")) return "🎧";
    if (name.includes("watch")) return "⌚";

    return "🛍️";
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, options);

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.message || data.error || "Request failed"
        );
    }

    return data;
}

// 1. PRODUCT SEARCH

async function searchProducts() {
    const keyword = searchInput.value.trim();

    if (!keyword) {
        resultMessage.textContent = "Please enter a product name.";
        productList.replaceChildren();
        return;
    }

    searchButton.disabled = true;
    searchButton.textContent = "Searching...";

    try {
        const products = await apiRequest(
            `${API_URL}/search?keyword=${encodeURIComponent(keyword)}`
        );

        if (!Array.isArray(products)) {
            throw new Error("Unexpected product response from server.");
        }

        allProducts = products;
        renderProducts(allProducts);

        resultMessage.textContent =
            `${allProducts.length} products found for "${keyword}".`;

    } catch (error) {
        productList.replaceChildren();
        resultMessage.textContent = error.message;
        console.error(error);

    } finally {
        searchButton.disabled = false;
        searchButton.textContent = "Search";
    }
}

searchButton.addEventListener("click", searchProducts);

searchInput.addEventListener("keydown", event => {
    if (event.key === "Enter") searchProducts();
});

// 2. DISPLAY PRODUCT CARDS

function renderProducts(products) {
    productList.replaceChildren();

    if (products.length === 0) {
        productList.appendChild(
            makeElement("p", "", "No products found.")
        );
        return;
    }

    products.forEach(product => {
        const card = makeElement("div", "product-card");

        card.appendChild(
            makeElement("div", "product-image", productEmoji(product))
        );

        card.appendChild(
            makeElement("h3", "", product.name || "Unnamed product")
        );

        card.appendChild(
            makeElement("p", "", `Product ID: ${product.id}`)
        );

        card.appendChild(
            makeElement("p", "", `Brand: ${product.brand || "N/A"}`)
        );

        card.appendChild(
            makeElement("p", "product-price", `₹${product.price}`)
        );

        card.appendChild(
            makeElement("p", "", `Rating: ${product.rating ?? "N/A"} / 5`)
        );

        const inStock = Number(product.stock) > 0;

        card.appendChild(
            makeElement(
                "p",
                inStock ? "stock-good" : "stock-bad",
                inStock ? "✓ Available" : "✕ Out of stock"
            )
        );

        // TRUST SCORE

        const trustButton = makeElement(
            "button",
            "trust-button",
            "🛡 Check Trust Score"
        );

        const trustResult = makeElement("div", "trust-result", "");
        trustResult.hidden = true;

        trustButton.addEventListener("click", async () => {
            trustButton.disabled = true;
            trustButton.textContent = "Calculating...";

            try {
                const data = await apiRequest(
                    `${API_URL}/trust-score?product_id=${encodeURIComponent(product.id)}`
                );

                trustResult.hidden = false;
                trustResult.textContent =
                    `${data.name || product.name}: ${data.trust_score}/100`;

            } catch (error) {
                trustResult.hidden = false;
                trustResult.textContent = error.message;

            } finally {
                trustButton.disabled = false;
                trustButton.textContent = "🛡 Check Trust Score";
            }
        });

        card.append(trustButton, trustResult);

        // COMPARISON AND CART BUTTONS

        const actions = makeElement("div", "product-actions");

        const compareButton = makeElement(
            "button",
            "",
            "⚖ Compare"
        );

        compareButton.addEventListener("click", () => {
            addToComparison(product);
        });

        const cartButton = makeElement(
            "button",
            "",
            "🛒 Add to Cart"
        );

        cartButton.addEventListener("click", () => {
            addToCart(product);
        });

        actions.append(compareButton, cartButton);
        card.appendChild(actions);

        productList.appendChild(card);
    });
}

// 3. BUDGET FILTER

document.getElementById("budgetButton").addEventListener("click", () => {
    const budgetInput = document.getElementById("budgetInput");
    const budget = Number(budgetInput.value);

    if (budgetInput.value.trim() === "" || budget < 0) {
        resultMessage.textContent = "Enter a valid budget.";
        return;
    }

    const filtered = allProducts.filter(
        product => Number(product.price) <= budget
    );

    renderProducts(filtered);

    resultMessage.textContent =
        `${filtered.length} products available within ₹${budget}.`;
});

document.getElementById("clearButton").addEventListener("click", () => {
    document.getElementById("budgetInput").value = "";
    renderProducts(allProducts);

    resultMessage.textContent =
        `${allProducts.length} products displayed.`;
});

// 4. PRODUCT COMPARISON

function addToComparison(product) {
    if (comparisonProducts.some(p => p.id === product.id)) {
        alert("This product is already selected.");
        return;
    }

    if (comparisonProducts.length >= 3) {
        alert("You can compare only three products at a time.");
        return;
    }

    comparisonProducts.push(product);
    renderComparison();
}

function renderComparison() {
    const container = document.getElementById("comparisonContent");
    container.replaceChildren();

    if (comparisonProducts.length === 0) {
        container.textContent = "Select products to compare.";
        return;
    }

    const table = document.createElement("table");

    const rows = [
        ["Product", p => p.name],
        ["Brand", p => p.brand],
        ["Price", p => `₹${p.price}`],
        ["Rating", p => `${p.rating} / 5`],
        ["Stock", p => Number(p.stock) > 0 ? "Available" : "Out of stock"]
    ];

    rows.forEach(([label, getter]) => {
        const tr = document.createElement("tr");
        const heading = makeElement("th", "", label);
        tr.appendChild(heading);

        comparisonProducts.forEach(product => {
            const cell = makeElement("td", "", getter(product));
            tr.appendChild(cell);
        });

        table.appendChild(tr);
    });

    container.appendChild(table);

    const clearButton = makeElement(
        "button",
        "light-button",
        "Clear Comparison"
    );

    clearButton.addEventListener("click", () => {
        comparisonProducts = [];
        renderComparison();
    });

    container.appendChild(clearButton);
}

// 5. SHOPPING CART

function addToCart(product) {
    if (Number(product.stock) <= 0) {
        alert("Sorry, this product is out of stock.");
        return;
    }

    const existing = cart.find(item => item.id === product.id);

    if (existing) {
        existing.quantity++;
    } else {
        cart.push({ ...product, quantity: 1 });
    }

    renderCart();
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    renderCart();
}

function renderCart() {
    const container = document.getElementById("cartContent");
    container.replaceChildren();

    const count = cart.reduce(
        (total, item) => total + item.quantity, 0
    );

    document.getElementById("cartCount").textContent = count;

    if (cart.length === 0) {
        container.textContent = "Your cart is empty.";
        return;
    }

    let total = 0;

    cart.forEach(item => {
        const itemTotal = Number(item.price) * item.quantity;
        total += itemTotal;

        const row = makeElement("div", "cart-item");
        const details = makeElement("div");

        details.appendChild(
            makeElement("strong", "", item.name)
        );

        details.appendChild(
            makeElement("p", "", `₹${item.price} × ${item.quantity}`)
        );

        const removeButton = makeElement(
            "button",
            "remove-button",
            "Remove"
        );

        removeButton.addEventListener("click", () => {
            removeFromCart(item.id);
        });

        row.append(details, removeButton);
        container.appendChild(row);
    });

    container.appendChild(
        makeElement("p", "cart-total", `Total: ₹${total.toFixed(2)}`)
    );
}

// 6. AI SHOPPING RECOMMENDATIONS

const aiButton = document.getElementById("aiButton");

aiButton.addEventListener("click", async () => {
    const query = document.getElementById("aiQuery").value.trim();
    const result = document.getElementById("aiResult");

    if (!query) {
        result.textContent = "Please enter your shopping requirements.";
        return;
    }

    aiButton.disabled = true;
    aiButton.textContent = "Finding products...";
    result.textContent = "Searching for recommendations...";

    try {
        const data = await apiRequest(`${API_URL}/recommend`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });

        result.replaceChildren();

        result.appendChild(
            makeElement("h2", "ai-heading", "🤖 Your Recommendations")
        );

        const recommendations = data.recommendations || [];

        result.appendChild(
            makeElement(
                "p",
                "ai-summary",
                `${recommendations.length} matching products found.`
            )
        );

        if (recommendations.length === 0) {
            result.appendChild(
                makeElement("p", "", "No matching products found.")
            );
            return;
        }

        const grid = makeElement("div", "ai-product-grid");

        recommendations.forEach(product => {
            const card = makeElement("div", "ai-product-card");

            card.appendChild(
                makeElement("div", "ai-product-icon", productEmoji(product))
            );

            card.appendChild(
                makeElement("h3", "", product.name)
            );

            card.appendChild(
                makeElement("p", "ai-price", `₹${product.price}`)
            );

            card.appendChild(
                makeElement("p", "ai-detail", `Brand: ${product.brand || "N/A"}`)
            );

            card.appendChild(
                makeElement("p", "ai-detail", `Rating: ${product.rating ?? "N/A"} / 5`)
            );

            card.appendChild(
                makeElement(
                    "p",
                    Number(product.stock) > 0 ? "stock-good" : "stock-bad",
                    Number(product.stock) > 0 ? "Available" : "Out of stock"
                )
            );

            grid.appendChild(card);
        });

        result.appendChild(grid);

    } catch (error) {
        result.textContent = error.message;
        console.error(error);

    } finally {
        aiButton.disabled = false;
        aiButton.textContent = "Get AI Recommendations →";
    }
});

renderCart();
renderComparison();

console.log("TRUSTBUY AI frontend initialized.");
