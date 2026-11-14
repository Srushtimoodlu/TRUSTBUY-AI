const API_URL = "http://127.0.0.1:5000";

const productList = document.getElementById("product-list");
const productMessage = document.getElementById("product-message");

let currentProducts = [];

// API request function
async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || data.message || "Request failed");
  }

  return data;
}

// Get products from API response
function getProducts(data) {
  if (Array.isArray(data)) return data;

  return data.products ||
    data.results ||
    data.items ||
    data.data ||
    [];
}

// Product details
function productId(product) {
  return product.product_id || product.id || "";
}

function productName(product) {
  return product.name || product.product_name || product.title || "Unnamed product";
}

function productPrice(product) {
  return Number(product.price || product.product_price || 0);
}

function formatPrice(value) {
  return "₹" + Number(value || 0).toLocaleString("en-IN");
}

// Safe HTML display
function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[character]);
}

function escapeJS(value) {
  return String(value ?? "").replace(/\\/g, "\\\\").replace(/'/g, "\\'");
}

function showMessage(message) {
  productMessage.textContent = message;
}

// 1. LOAD PRODUCTS
async function loadProducts() {
  productList.innerHTML = "<p>Loading products...</p>";

  try {
    const data = await apiRequest("/products");
    currentProducts = getProducts(data);
    displayProducts(currentProducts);
    loadCategories();
  } catch (error) {
    productList.innerHTML =
      "<p>Unable to load products. Check whether the backend is running.</p>";
    showMessage(error.message);
  }
}

// 2. DISPLAY PRODUCTS
function displayProducts(products) {
  currentProducts = products;

  document.getElementById("result-count").textContent =
    `${products.length} product(s) found`;

  if (!products.length) {
    productList.innerHTML = "<p>No products found.</p>";
    return;
  }

  productList.innerHTML = products.map(product => {
    const id = productId(product);
    const name = productName(product);
    const price = productPrice(product);
    const category = product.category || "Product";
    const description = product.description || "Explore product details.";

    return `
      <div class="product-card">
        <div class="product-top">
          <span class="product-category">${escapeHTML(category)}</span>
          <span class="product-id">${escapeHTML(id)}</span>
        </div>

        <h3>${escapeHTML(name)}</h3>
        <p class="product-description">${escapeHTML(description)}</p>

        <div class="product-price">${formatPrice(price)}</div>

        <div class="product-actions">
          <button class="small-button"
            onclick="viewTrust('${escapeJS(id)}')">
            Trust Details
          </button>

          <button class="small-button"
            onclick="checkStock('${escapeJS(id)}')">
            Check Stock
          </button>

          <button class="primary-button"
            onclick="addToCart('${escapeJS(id)}')">
            Add to Cart
          </button>
        </div>
      </div>
    `;
  }).join("");
}

// 3. PRODUCT SEARCH
async function searchProducts() {
  const keyword = document.getElementById("search-input").value.trim();

  if (!keyword) {
    loadProducts();
    return;
  }

  try {
    const data = await apiRequest(
      `/search?keyword=${encodeURIComponent(keyword)}`
    );

    displayProducts(getProducts(data));
    showMessage(`Search results for ${keyword}`);
  } catch (error) {
    showMessage(error.message);
  }
}

// 4. BUDGET FILTER
async function filterByBudget() {
  const amount = document.getElementById("budget-input").value;

  if (!amount || Number(amount) <= 0) {
    showMessage("Enter a valid budget.");
    return;
  }

  try {
    const data = await apiRequest(
      `/budget?amount=${encodeURIComponent(amount)}`
    );

    displayProducts(getProducts(data));
    showMessage(`Products within ${formatPrice(amount)}`);
  } catch (error) {
    showMessage(error.message);
  }
}

// 5. CATEGORY FILTER
async function filterByCategory() {
  const category = document.getElementById("category-select").value;

  if (!category) {
    loadProducts();
    return;
  }

  try {
    const data = await apiRequest(
      `/category?name=${encodeURIComponent(category)}`
    );

    displayProducts(getProducts(data));
    showMessage(`Category: ${category}`);
  } catch (error) {
    showMessage(error.message);
  }
}

// Load categories
async function loadCategories() {
  const select = document.getElementById("category-select");

  try {
    const data = await apiRequest("/categories");

    let categories = Array.isArray(data)
      ? data
      : data.categories || [];

    categories = categories.map(item =>
      typeof item === "string" ? item : item.name || item.category
    ).filter(Boolean);

    select.innerHTML = '<option value="">All categories</option>';

    categories.forEach(category => {
      const option = document.createElement("option");
      option.value = category;
      option.textContent = category;
      select.appendChild(option);
    });
  } catch (error) {
    console.warn("Category loading:", error.message);
  }
}

// 6. SORT PRODUCTS
async function sortProducts() {
  const order = document.getElementById("sort-select").value;

  if (!order) {
    loadProducts();
    return;
  }

  try {
    const data = await apiRequest(
      `/sort?order=${encodeURIComponent(order)}`
    );

    displayProducts(getProducts(data));
  } catch (error) {
    showMessage(error.message);
  }
}

// Apply filters
async function applyFilters() {
  const budget = document.getElementById("budget-input").value;
  const category = document.getElementById("category-select").value;

  if (budget) {
    await filterByBudget();
  } else if (category) {
    await filterByCategory();
  } else {
    await loadProducts();
  }

  const order = document.getElementById("sort-select").value;

  if (order) {
    currentProducts.sort((a, b) =>
      order === "low-to-high"
        ? productPrice(a) - productPrice(b)
        : productPrice(b) - productPrice(a)
    );

    displayProducts(currentProducts);
  }
}

// 7. PRODUCT COMPARISON
async function compareProducts() {
  const ids = document.getElementById("compare-ids").value.trim();

  if (!ids) {
    alert("Enter product IDs separated by commas.");
    return;
  }

  const result = document.getElementById("comparison-result");
  result.innerHTML = "<p>Comparing products...</p>";

  try {
    const data = await apiRequest(
      `/compare?ids=${encodeURIComponent(ids)}`
    );

    const products = getProducts(data);

    if (!products.length) {
      result.textContent = JSON.stringify(data, null, 2);
      return;
    }

    result.innerHTML = `
      <h3>Comparison Results</h3>

      <table class="data-table">
        <thead>
          <tr>
            <th>Product</th>
            <th>Price</th>
            <th>Category</th>
          </tr>
        </thead>

        <tbody>
          ${products.map(product => `
            <tr>
              <td>${escapeHTML(productName(product))}</td>
              <td>${formatPrice(productPrice(product))}</td>
              <td>${escapeHTML(product.category || "—")}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  } catch (error) {
    result.textContent = error.message;
  }
}

// 8. TRUST SCORE AND DETAILS
async function viewTrust(id) {
  document.getElementById("trust-product-id").value = id;

  const result = document.getElementById("trust-result");
  result.innerHTML = "<p>Loading trust information...</p>";

  try {
    const [scoreResult, sellerResult, reviewResult] =
      await Promise.allSettled([
        apiRequest(`/trust-score?product_id=${encodeURIComponent(id)}`),
        apiRequest(`/seller?product_id=${encodeURIComponent(id)}`),
        apiRequest(`/reviews?product_id=${encodeURIComponent(id)}`)
      ]);

    const scoreData = scoreResult.status === "fulfilled"
      ? scoreResult.value : null;

    const sellerData = sellerResult.status === "fulfilled"
      ? sellerResult.value : null;

    const reviewData = reviewResult.status === "fulfilled"
      ? reviewResult.value : null;

    const rawScore = scoreData?.trust_score ??
      scoreData?.score ??
      scoreData?.total_score;

    const score = Number(rawScore);

    const validScore = rawScore !== undefined &&
      rawScore !== null &&
      Number.isFinite(score) &&
      score >= 0 &&
      score <= 100;

    const reviews = Array.isArray(reviewData)
      ? reviewData
      : reviewData?.reviews || [];

    const seller = sellerData?.seller || sellerData || {};

    result.innerHTML = `
      <h3>Trust Information: ${escapeHTML(id)}</h3>

      ${validScore ? `
        <div class="score-display">
          <div class="score-number">
            ${score.toFixed(1)}<small>/100</small>
          </div>

          <div>
            <strong>Product Trust Score</strong>
            <p class="muted">Based on available prototype data.</p>
          </div>
        </div>

        <div class="trust-bar">
          <span style="width:${score}%"></span>
        </div>
      ` : "<p>Trust score is not available.</p>"}

      <h3>Seller Information</h3>
      <p><strong>Seller:</strong>
        ${escapeHTML(seller.name || seller.seller_name || "Not available")}
      </p>

      <p><strong>Seller Rating:</strong>
        ${escapeHTML(seller.rating ?? seller.seller_rating ?? "Not available")}
      </p>

      <p><strong>Verification:</strong>
        ${escapeHTML(seller.verified ?? seller.is_verified ?? seller.verification_status ?? "Not available")}
      </p>

      <h3>Customer Reviews</h3>

      ${reviews.length ? reviews.map(review => `
        <p>
          ★ ${escapeHTML(review.rating ?? "—")} -
          ${escapeHTML(review.comment || review.review || review.text || "Review information")}
        </p>
      `).join("") : "<p>Review details are not available.</p>"}
    `;

    document.getElementById("trust").scrollIntoView({
      behavior: "smooth"
    });

  } catch (error) {
    result.textContent = error.message;
  }
}

// Trust details search
async function searchTrustDetails() {
  const id = document.getElementById("trust-product-id").value.trim();

  if (!id) {
    alert("Enter a product ID.");
    return;
  }

  await viewTrust(id);
}

// 9. INVENTORY CHECK
async function checkStock(id) {
  try {
    const data = await apiRequest(
      `/stock?product_id=${encodeURIComponent(id)}`
    );

    alert("Inventory Information:\n" + JSON.stringify(data, null, 2));
  } catch (error) {
    alert("Stock check failed: " + error.message);
  }
}

// 10. ADD TO CART WITH CONFIRMATION
async function addToCart(id) {
  const product = currentProducts.find(
    item => productId(item) === id
  );

  const name = product ? productName(product) : id;

  const confirmed = window.confirm(
    `Do you want to add ${name} to your cart?`
  );

  if (!confirmed) return;

  try {
    await apiRequest("/cart/add", {
      method: "POST",
      body: JSON.stringify({
        product_id: id,
        quantity: 1
      })
    });

    alert("Product added to cart.");
    loadCart();

  } catch (error) {
    alert("Unable to add product: " + error.message);
  }
}

// 11. VIEW CART
async function loadCart() {
  const container = document.getElementById("cart-result");

  try {
    const data = await apiRequest("/cart");
    const items = getProducts(data);

    document.getElementById("cart-count").textContent =
      items.reduce(
        (total, item) => total + Number(item.quantity || 1),
        0
      );

    if (!items.length) {
      container.innerHTML = "<p>Your cart is empty.</p>";
      return;
    }

    const total = data.total ?? data.total_price ??
      items.reduce(
        (sum, item) =>
          sum + productPrice(item) * Number(item.quantity || 1),
        0
      );

    container.innerHTML = `
      <h3>Your Selected Products</h3>

      ${items.map(item => {
        const id = productId(item);
        const name = productName(item);
        const quantity = Number(item.quantity || 1);

        return `
          <div class="cart-item">
            <div>
              <strong>${escapeHTML(name)}</strong>
              <p>${escapeHTML(id)} · Quantity: ${quantity}</p>
              <p>${formatPrice(productPrice(item) * quantity)}</p>
            </div>

            <button onclick="removeFromCart('${escapeJS(id)}')">
              Remove
            </button>
          </div>
        `;
      }).join("")}

      <p class="cart-total">Total: ${formatPrice(total)}</p>
    `;

  } catch (error) {
    container.textContent = "Unable to load cart: " + error.message;
  }
}

// 12. REMOVE FROM CART
async function removeFromCart(id) {
  const confirmed = window.confirm(
    "Do you want to remove this product?"
  );

  if (!confirmed) return;

  try {
    await apiRequest("/cart/remove", {
      method: "DELETE",
      body: JSON.stringify({
        product_id: id
      })
    });

    alert("Product removed from cart.");
    loadCart();

  } catch (error) {
    alert("Unable to remove product: " + error.message);
  }
}

// BUTTON EVENT LISTENERS

document.getElementById("search-btn")
  .addEventListener("click", searchProducts);

document.getElementById("search-input")
  .addEventListener("keydown", event => {
    if (event.key === "Enter") searchProducts();
  });

document.getElementById("show-all-btn")
  .addEventListener("click", () => {
    document.getElementById("search-input").value = "";
    document.getElementById("budget-input").value = "";
    document.getElementById("category-select").value = "";
    document.getElementById("sort-select").value = "";
    loadProducts();
  });

document.getElementById("filter-btn")
  .addEventListener("click", applyFilters);

document.getElementById("sort-select")
  .addEventListener("change", sortProducts);

document.getElementById("compare-btn")
  .addEventListener("click", compareProducts);

document.getElementById("trust-btn")
  .addEventListener("click", searchTrustDetails);

document.getElementById("refresh-cart-btn")
  .addEventListener("click", loadCart);

// START WEBSITE
loadProducts();
loadCart();