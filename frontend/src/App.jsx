import { useEffect, useState } from "react";

import {
  Activity,
  Boxes,
  LayoutDashboard,
  Package,
  ShoppingCart,
  Truck,
  Users,
  AlertTriangle,
  RefreshCw,
  Bot,
  ClipboardList,
  Menu,
  X,
  Moon,
  Sun,
  Plus,
  Search,
  Pencil,
  Ban,
  ArrowLeft,
  CheckCircle2,
  IndianRupee,
  History,
  ArrowDownToLine,
  ArrowUpFromLine,
  Clock,
} from "lucide-react";

import api from "./services/api";
import "./App.css";
import PurchaseOrdersPage from "./PurchaseOrdersPage";
import SalesOrdersPage from "./SalesOrdersPage";
import AIAssistantPage from "./AIAssistantPage";

/* =========================================
   NAVIGATION
========================================= */

const navigation = [
  { label: "Dashboard", icon: LayoutDashboard },
  { label: "Products", icon: Package },
  { label: "Inventory", icon: Boxes },
  { label: "Suppliers", icon: Truck },
  { label: "Purchase Orders", icon: ClipboardList },
  { label: "Sales Orders", icon: ShoppingCart },
  { label: "AI Assistant", icon: Bot },
];

const emptyProduct = {
  sku: "",
  name: "",
  description: "",
  price: "",
  quantity: "",
};

const emptySupplier = {
  name: "",
  contact_person: "",
  email: "",
  phone: "",
  address: "",
};

/* =========================================
   SHARED UTILITIES
========================================= */

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(Number(value ?? 0));
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function getErrorMessage(error, fallback) {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(", ");
  }

  return error.message || fallback;
}

function ErrorBanner({ message, onDismiss }) {
  if (!message) return null;

  return (
    <div className="form-error" role="alert">
      <AlertTriangle size={18} />
      <span>{message}</span>

      {onDismiss && (
        <button type="button" onClick={onDismiss}>
          Dismiss
        </button>
      )}
    </div>
  );
}

function SuccessBanner({ message, onDismiss }) {
  if (!message) return null;

  return (
    <div className="form-success" role="status">
      <CheckCircle2 size={18} />
      <span>{message}</span>

      {onDismiss && (
        <button type="button" onClick={onDismiss}>
          Dismiss
        </button>
      )}
    </div>
  );
}

function LoadingPanel({ message = "Loading data..." }) {
  return (
    <div className="loading-panel">
      <RefreshCw size={23} className="spin" />
      <p>{message}</p>
    </div>
  );
}

function EmptyState({ title, description, icon: Icon = Package }) {
  return (
    <div className="empty-state">
      <Icon size={28} />
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function DashboardCard({
  title,
  value,
  subtitle,
  icon: Icon,
  accent,
}) {
  return (
    <article className="metric-card">
      <div className={`metric-icon ${accent}`}>
        <Icon size={21} />
      </div>

      <p className="metric-title">{title}</p>
      <h2>{value}</h2>
      <p className="metric-subtitle">{subtitle}</p>
    </article>
  );
}

/* =========================================
   REUSABLE SEARCH FIELD
========================================= */

function SearchField({ value, onChange, placeholder }) {
  return (
    <label className="search-box">
      <Search size={17} />

      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        aria-label={placeholder}
      />
    </label>
  );
}

/* =========================================
   PRODUCT FORM
========================================= */

function ProductForm({
  product,
  onSave,
  onCancel,
  saving,
  error,
}) {
  const [form, setForm] = useState(() =>
    product
      ? {
          sku: product.sku ?? "",
          name: product.name ?? "",
          description: product.description ?? "",
          price: String(product.price ?? ""),
          quantity: String(product.quantity ?? ""),
        }
      : { ...emptyProduct }
  );

  function updateField(event) {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  function submit(event) {
    event.preventDefault();

    const price = Number(form.price);
    const quantity = Number(form.quantity);

    if (!form.name.trim() || !form.sku.trim()) {
      return;
    }

    if (!Number.isFinite(price) || price < 0) {
      return;
    }

    if (!Number.isInteger(quantity) || quantity < 0) {
      return;
    }

    onSave({
      sku: form.sku.trim(),
      name: form.name.trim(),
      description: form.description.trim(),
      price,
      quantity,
    });
  }

  return (
    <section className="product-form-panel">
      <div className="form-heading">
        <button
          type="button"
          className="back-button"
          onClick={onCancel}
          disabled={saving}
        >
          <ArrowLeft size={17} />
          Back to products
        </button>

        <h2>
          {product ? "Edit product" : "Add a new product"}
        </h2>

        <p>
          {product
            ? "Update the product information."
            : "Enter the details of your new product."}
        </p>
      </div>

      <ErrorBanner message={error} />

      <form className="product-form" onSubmit={submit}>
        <label>
          Product name <span>*</span>

          <input
            name="name"
            value={form.name}
            onChange={updateField}
            placeholder="Product name"
            required
          />
        </label>

        <label>
          SKU <span>*</span>

          <input
            name="sku"
            value={form.sku}
            onChange={updateField}
            placeholder="SKU-001"
            required
          />
        </label>

        <label className="full-width">
          Description

          <textarea
            name="description"
            value={form.description}
            onChange={updateField}
            placeholder="Product description"
            rows={3}
          />
        </label>

        <label>
          Unit price (₹) <span>*</span>

          <input
            type="number"
            name="price"
            value={form.price}
            onChange={updateField}
            min="0"
            step="0.01"
            required
          />
        </label>

        <label>
          Quantity <span>*</span>

          <input
            type="number"
            name="quantity"
            value={form.quantity}
            onChange={updateField}
            min="0"
            step="1"
            required
          />
        </label>

        <div className="form-actions full-width">
          <button
            type="button"
            className="secondary-button"
            onClick={onCancel}
            disabled={saving}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="primary-button"
            disabled={saving}
          >
            {saving
              ? "Saving..."
              : product
                ? "Save changes"
                : "Create product"}
          </button>
        </div>
      </form>
    </section>
  );
}

/* =========================================
   PRODUCTS PAGE
========================================= */

function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [search, setSearch] = useState("");
  const [showInactive, setShowInactive] = useState(false);
  const [formProduct, setFormProduct] = useState(undefined);

  async function loadProducts() {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/products/");

      if (!Array.isArray(response.data)) {
        throw new Error("Unexpected products API response.");
      }

      setProducts(response.data);
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to load products.")
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProducts();
  }, []);

  async function saveProduct(payload) {
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      if (formProduct) {
        await api.put(
          `/products/${formProduct.id}`,
          payload
        );

        setSuccess("Product updated successfully.");
      } else {
        await api.post("/products/", payload);
        setSuccess("Product created successfully.");
      }

      setFormProduct(undefined);
      await loadProducts();
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to save the product.")
      );
    } finally {
      setSaving(false);
    }
  }

  async function deactivateProduct(product) {
    const confirmed = window.confirm(
      `Deactivate "${product.name}"?`
    );

    if (!confirmed) return;

    setError("");
    setSuccess("");

    try {
      await api.delete(`/products/${product.id}`);

      setSuccess(`${product.name} was deactivated.`);
      await loadProducts();
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to deactivate product.")
      );
    }
  }

  const filteredProducts = products.filter((product) => {
    const query = search.toLowerCase();

    const matchesSearch = [
      product.name,
      product.sku,
      product.description,
    ]
      .filter(Boolean)
      .some((value) =>
        String(value).toLowerCase().includes(query)
      );

    return (
      matchesSearch &&
      (showInactive || product.is_active !== false)
    );
  });

  const activeCount = products.filter(
    (product) => product.is_active !== false
  ).length;

  if (formProduct !== undefined) {
    return (
      <ProductForm
        key={formProduct?.id ?? "new-product"}
        product={formProduct}
        onSave={saveProduct}
        onCancel={() => {
          setFormProduct(undefined);
          setError("");
        }}
        saving={saving}
        error={error}
      />
    );
  }

  return (
    <div className="products-page">
      <div className="products-toolbar">
        <div>
          <h2>Product catalog</h2>
          <p>Manage the products your business sells.</p>
        </div>

        <button
          className="primary-button"
          onClick={() => {
            setError("");
            setSuccess("");
            setFormProduct(null);
          }}
        >
          <Plus size={17} />
          Add product
        </button>
      </div>

      <ErrorBanner
        message={error}
        onDismiss={() => setError("")}
      />

      <SuccessBanner
        message={success}
        onDismiss={() => setSuccess("")}
      />

      <div className="product-summary-grid">
        <article className="product-summary-card">
          <span>Total products returned</span>
          <strong>{products.length}</strong>
        </article>

        <article className="product-summary-card">
          <span>Active products</span>
          <strong>{activeCount}</strong>
        </article>

        <article className="product-summary-card">
          <span>Inactive products</span>
          <strong>{products.length - activeCount}</strong>
        </article>
      </div>

      <section className="product-table-panel">
        <div className="product-table-toolbar">
          <div>
            <h3>All products</h3>
            <p>Search and manage your product catalog.</p>
          </div>

          <div className="product-filters">
            <SearchField
              value={search}
              onChange={setSearch}
              placeholder="Search products..."
            />

            <label className="inactive-toggle">
              <input
                type="checkbox"
                checked={showInactive}
                onChange={(event) =>
                  setShowInactive(event.target.checked)
                }
              />
              Show inactive
            </label>

            <button
              className="icon-button"
              onClick={loadProducts}
              disabled={loading}
              aria-label="Refresh products"
            >
              <RefreshCw
                size={17}
                className={loading ? "spin" : ""}
              />
            </button>
          </div>
        </div>

        {loading ? (
          <LoadingPanel message="Loading products..." />
        ) : filteredProducts.length === 0 ? (
          <EmptyState
            title="No products found"
            description="Try another search or add a product."
          />
        ) : (
          <div className="table-wrapper">
            <table className="products-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>SKU</th>
                  <th>Unit price</th>
                  <th>Quantity</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredProducts.map((product) => (
                  <tr key={product.id}>
                    <td>
                      <div className="product-name-cell">
                        <div className="product-avatar">
                          <Package size={18} />
                        </div>

                        <div>
                          <strong>{product.name}</strong>
                          <span>
                            {product.description || "No description"}
                          </span>
                        </div>
                      </div>
                    </td>

                    <td>{product.sku}</td>
                    <td>{formatCurrency(product.price)}</td>
                    <td>{product.quantity}</td>

                    <td>
                      <span
                        className={`product-status ${
                          product.is_active === false
                            ? "inactive"
                            : "active"
                        }`}
                      >
                        {product.is_active === false
                          ? "Inactive"
                          : "Active"}
                      </span>
                    </td>

                    <td>
                      <div className="product-actions">
                        <button
                          className="icon-button"
                          title="Edit product"
                          aria-label={`Edit ${product.name}`}
                          onClick={() => {
                            setError("");
                            setSuccess("");
                            setFormProduct(product);
                          }}
                        >
                          <Pencil size={16} />
                        </button>

                        {product.is_active !== false && (
                          <button
                            className="icon-button danger-button"
                            title="Deactivate product"
                            aria-label={`Deactivate ${product.name}`}
                            onClick={() =>
                              deactivateProduct(product)
                            }
                          >
                            <Ban size={16} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="product-table-footer">
          Showing {filteredProducts.length} of {products.length} products
        </div>
      </section>
    </div>
  );
}

/* =========================================
   INVENTORY PAGE
========================================= */

function InventoryPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showInactive, setShowInactive] = useState(false);

  const [selectedProduct, setSelectedProduct] = useState(null);
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const [quantityChange, setQuantityChange] = useState("");
  const [reason, setReason] = useState("");
  const [adjusting, setAdjusting] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadProducts() {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/products/");
      setProducts(response.data);
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to load inventory.")
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadHistory(product) {
    setSelectedProduct(product);
    setHistory([]);
    setHistoryLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await api.get(
        `/inventory/${product.id}/history`
      );

      setHistory(response.data);
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to load inventory history.")
      );
    } finally {
      setHistoryLoading(false);
    }
  }

  useEffect(() => {
    loadProducts();
  }, []);

  async function adjustStock(event) {
    event.preventDefault();

    if (!selectedProduct) return;

    const change = Number(quantityChange);

    if (!Number.isInteger(change) || change === 0) {
      setError(
        "Enter a non-zero whole number. Positive adds stock; negative removes stock."
      );
      return;
    }

    if (!reason.trim()) {
      setError("Please enter a reason for the adjustment.");
      return;
    }

    if (selectedProduct.is_active === false) {
      setError(
        "Inactive products cannot have inventory adjusted."
      );
      return;
    }

    if (
      Number(selectedProduct.quantity) + change < 0
    ) {
      setError("Stock cannot become negative.");
      return;
    }

    setAdjusting(true);
    setError("");
    setSuccess("");

    try {
      await api.post("/inventory/adjust", {
        product_id: selectedProduct.id,
        quantity_change: change,
        reason: reason.trim(),
      });

      setSuccess(
        `Stock adjusted successfully. ${
          change > 0 ? "Added" : "Removed"
        } ${Math.abs(change)} units.`
      );

      setQuantityChange("");
      setReason("");

      const [productsResponse, historyResponse] =
        await Promise.all([
          api.get("/products/"),
          api.get(
            `/inventory/${selectedProduct.id}/history`
          ),
        ]);

      setProducts(productsResponse.data);
      setHistory(historyResponse.data);

      const updatedProduct = productsResponse.data.find(
        (item) => item.id === selectedProduct.id
      );

      if (updatedProduct) {
        setSelectedProduct(updatedProduct);
      }
    } catch (err) {
      setError(
        getErrorMessage(err, "Inventory adjustment failed.")
      );
    } finally {
      setAdjusting(false);
    }
  }

  const activeProducts = products.filter(
    (product) => product.is_active !== false
  );

  const totalUnits = activeProducts.reduce(
    (sum, product) =>
      sum + Number(product.quantity ?? 0),
    0
  );

  const totalValue = activeProducts.reduce(
    (sum, product) =>
      sum +
      Number(product.price ?? 0) *
        Number(product.quantity ?? 0),
    0
  );

  const lowStockProducts = activeProducts.filter(
    (product) => Number(product.quantity ?? 0) <= 5
  );

  const filteredProducts = products.filter((product) => {
    const query = search.toLowerCase();

    const matchesSearch =
      String(product.name ?? "").toLowerCase().includes(query) ||
      String(product.sku ?? "").toLowerCase().includes(query);

    return (
      matchesSearch &&
      (showInactive || product.is_active !== false)
    );
  });

  return (
    <div className="inventory-page">
      <div className="products-toolbar">
        <div>
          <h2>Inventory management</h2>
          <p>Monitor quantities and track stock movements.</p>
        </div>

        <button
          className="secondary-button"
          onClick={loadProducts}
          disabled={loading}
        >
          <RefreshCw
            size={16}
            className={loading ? "spin" : ""}
          />
          Refresh inventory
        </button>
      </div>

      <ErrorBanner
        message={error}
        onDismiss={() => setError("")}
      />

      <SuccessBanner
        message={success}
        onDismiss={() => setSuccess("")}
      />

      <div className="product-summary-grid inventory-summary-grid">
        <article className="product-summary-card">
          <span>Active products</span>
          <strong>{activeProducts.length}</strong>
        </article>

        <article className="product-summary-card">
          <span>Total units in stock</span>
          <strong>{totalUnits.toLocaleString("en-IN")}</strong>
        </article>

        <article className="product-summary-card">
          <span>Inventory value</span>
          <strong>{formatCurrency(totalValue)}</strong>
        </article>

        <article className="product-summary-card">
          <span>Low-stock products</span>
          <strong>{lowStockProducts.length}</strong>
        </article>
      </div>

      <section className="product-table-panel">
        <div className="product-table-toolbar">
          <div>
            <h3>Stock overview</h3>
            <p>Select a product to adjust stock or view its history.</p>
          </div>

          <div className="product-filters">
            <SearchField
              value={search}
              onChange={setSearch}
              placeholder="Search inventory..."
            />

            <label className="inactive-toggle">
              <input
                type="checkbox"
                checked={showInactive}
                onChange={(event) =>
                  setShowInactive(event.target.checked)
                }
              />
              Show inactive
            </label>
          </div>
        </div>

        {loading ? (
          <LoadingPanel message="Loading inventory..." />
        ) : filteredProducts.length === 0 ? (
          <EmptyState
            title="No inventory items found"
            description="Try another search or change the inactive filter."
            icon={Boxes}
          />
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>SKU</th>
                  <th>Quantity</th>
                  <th>Unit price</th>
                  <th>Stock value</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {filteredProducts.map((product) => {
                  const quantity = Number(product.quantity ?? 0);
                  const active = product.is_active !== false;

                  return (
                    <tr key={product.id}>
                      <td>{product.name}</td>
                      <td>{product.sku}</td>
                      <td>{quantity}</td>
                      <td>{formatCurrency(product.price)}</td>

                      <td>
                        {formatCurrency(
                          Number(product.price ?? 0) * quantity
                        )}
                      </td>

                      <td>
                        <span
                          className={`product-status ${
                            !active
                              ? "inactive"
                              : quantity <= 5
                                ? "inactive"
                                : "active"
                          }`}
                        >
                          {!active
                            ? "Inactive"
                            : quantity <= 5
                              ? "Low stock"
                              : "In stock"}
                        </span>
                      </td>

                      <td>
                        <button
                          className="secondary-button inventory-view-button"
                          onClick={() => loadHistory(product)}
                        >
                          <History size={15} />
                          History
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        <div className="product-table-footer">
          Showing {filteredProducts.length} of {products.length} products
        </div>
      </section>

      {selectedProduct && (
        <section className="product-form-panel inventory-detail-panel">
          <div className="form-heading">
            <button
              className="back-button"
              onClick={() => {
                setSelectedProduct(null);
                setHistory([]);
                setError("");
                setSuccess("");
              }}
            >
              <ArrowLeft size={17} />
              Close inventory details
            </button>

            <h2>{selectedProduct.name}</h2>

            <p>
              SKU: {selectedProduct.sku} · Current stock:{" "}
              {selectedProduct.quantity}
            </p>
          </div>

          {selectedProduct.is_active === false ? (
            <div className="inactive-product-notice">
              <AlertTriangle size={18} />
              This product is inactive. Stock adjustments are disabled.
            </div>
          ) : (
            <form
              className="inventory-adjust-form"
              onSubmit={adjustStock}
            >
              <div>
                <h3>Adjust stock</h3>
                <p>
                  Positive numbers add stock. Negative numbers remove stock.
                </p>
              </div>

              <label>
                Quantity change

                <input
                  type="number"
                  step="1"
                  required
                  value={quantityChange}
                  onChange={(event) =>
                    setQuantityChange(event.target.value)
                  }
                  placeholder="e.g. 5 or -2"
                />
              </label>

              <label>
                Reason

                <input
                  type="text"
                  required
                  value={reason}
                  onChange={(event) =>
                    setReason(event.target.value)
                  }
                  placeholder="Reason for adjustment"
                />
              </label>

              <button
                type="submit"
                className="primary-button"
                disabled={adjusting}
              >
                {adjusting ? (
                  <RefreshCw size={16} className="spin" />
                ) : Number(quantityChange) > 0 ? (
                  <ArrowDownToLine size={16} />
                ) : (
                  <ArrowUpFromLine size={16} />
                )}

                {adjusting
                  ? "Adjusting..."
                  : "Apply adjustment"}
              </button>
            </form>
          )}

          <div className="history-section">
            <div className="history-heading">
              <div>
                <h3>
                  <History size={18} />
                  Stock movement history
                </h3>

                <p>Recorded inventory adjustments.</p>
              </div>

              <button
                className="icon-button"
                onClick={() => loadHistory(selectedProduct)}
                disabled={historyLoading}
                aria-label="Refresh history"
              >
                <RefreshCw
                  size={16}
                  className={historyLoading ? "spin" : ""}
                />
              </button>
            </div>

            {historyLoading ? (
              <LoadingPanel message="Loading transaction history..." />
            ) : history.length === 0 ? (
              <EmptyState
                title="No recorded stock movements"
                description="No inventory transactions were returned for this product."
                icon={Clock}
              />
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Change</th>
                      <th>Before</th>
                      <th>After</th>
                      <th>Reason</th>
                    </tr>
                  </thead>

                  <tbody>
                    {history.map((item) => (
                      <tr key={item.id}>
                        <td>{formatDate(item.created_at)}</td>

                        <td>
                          <span
                            className={`quantity-change ${
                              item.quantity_change > 0
                                ? "quantity-increase"
                                : "quantity-decrease"
                            }`}
                          >
                            {item.quantity_change > 0 ? "+" : ""}
                            {item.quantity_change}
                          </span>
                        </td>

                        <td>{item.quantity_before}</td>
                        <td>{item.quantity_after}</td>
                        <td>{item.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}

/* =========================================
   SUPPLIER FORM
========================================= */

function SupplierForm({
  supplier,
  onSave,
  onCancel,
  saving,
  error,
}) {
  const [form, setForm] = useState(() =>
    supplier
      ? {
          name: supplier.name ?? "",
          contact_person: supplier.contact_person ?? "",
          email: supplier.email ?? "",
          phone: supplier.phone ?? "",
          address: supplier.address ?? "",
        }
      : { ...emptySupplier }
  );

  function updateField(event) {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  function submit(event) {
    event.preventDefault();

    if (!form.name.trim()) return;

    onSave({
      name: form.name.trim(),
      contact_person: form.contact_person.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      address: form.address.trim(),
    });
  }

  return (
    <section className="product-form-panel">
      <div className="form-heading">
        <button
          type="button"
          className="back-button"
          onClick={onCancel}
          disabled={saving}
        >
          <ArrowLeft size={17} />
          Back to suppliers
        </button>

        <h2>
          {supplier ? "Edit supplier" : "Add a new supplier"}
        </h2>

        <p>
          {supplier
            ? "Update the supplier's contact information."
            : "Register a new supplier for your business."}
        </p>
      </div>

      <ErrorBanner message={error} />

      <form className="product-form" onSubmit={submit}>
        <label>
          Supplier name <span>*</span>

          <input
            name="name"
            value={form.name}
            onChange={updateField}
            placeholder="Supplier or company name"
            required
          />
        </label>

        <label>
          Contact person

          <input
            name="contact_person"
            value={form.contact_person}
            onChange={updateField}
            placeholder="Contact person's name"
          />
        </label>

        <label>
          Email

          <input
            type="email"
            name="email"
            value={form.email}
            onChange={updateField}
            placeholder="supplier@example.com"
          />
        </label>

        <label>
          Phone

          <input
            type="tel"
            name="phone"
            value={form.phone}
            onChange={updateField}
            placeholder="Phone number"
          />
        </label>

        <label className="full-width">
          Address

          <textarea
            name="address"
            value={form.address}
            onChange={updateField}
            placeholder="Supplier's address"
            rows={3}
          />
        </label>

        <div className="form-actions full-width">
          <button
            type="button"
            className="secondary-button"
            onClick={onCancel}
            disabled={saving}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="primary-button"
            disabled={saving}
          >
            {saving
              ? "Saving..."
              : supplier
                ? "Save changes"
                : "Create supplier"}
          </button>
        </div>
      </form>
    </section>
  );
}

/* =========================================
   SUPPLIERS PAGE
========================================= */

function SuppliersPage() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [search, setSearch] = useState("");
  const [showInactive, setShowInactive] = useState(false);
  const [formSupplier, setFormSupplier] = useState(undefined);

  async function loadSuppliers() {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/suppliers/");

      if (!Array.isArray(response.data)) {
        throw new Error("Unexpected suppliers API response.");
      }

      setSuppliers(response.data);
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to load suppliers.")
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSuppliers();
  }, []);

  async function saveSupplier(payload) {
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      if (formSupplier) {
        await api.put(
          `/suppliers/${formSupplier.id}`,
          payload
        );

        setSuccess("Supplier updated successfully.");
      } else {
        await api.post("/suppliers/", payload);
        setSuccess("Supplier created successfully.");
      }

      setFormSupplier(undefined);
      await loadSuppliers();
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to save supplier.")
      );
    } finally {
      setSaving(false);
    }
  }

  async function deleteSupplier(supplier) {
    const confirmed = window.confirm(
      `Delete supplier "${supplier.name}"?`
    );

    if (!confirmed) return;

    setError("");
    setSuccess("");

    try {
      await api.delete(`/suppliers/${supplier.id}`);

      setSuccess(
        `Supplier "${supplier.name}" deleted successfully.`
      );

      await loadSuppliers();
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          "Unable to delete supplier. The supplier may be referenced by a purchase order."
        )
      );
    }
  }

  const filteredSuppliers = suppliers.filter((supplier) => {
    const query = search.toLowerCase();

    const matchesSearch = [
      supplier.name,
      supplier.contact_person,
      supplier.email,
      supplier.phone,
      supplier.address,
    ]
      .filter(Boolean)
      .some((value) =>
        String(value).toLowerCase().includes(query)
      );

    return (
      matchesSearch &&
      (showInactive || supplier.is_active !== false)
    );
  });

  const activeCount = suppliers.filter(
    (supplier) => supplier.is_active !== false
  ).length;

  if (formSupplier !== undefined) {
    return (
      <SupplierForm
        key={formSupplier?.id ?? "new-supplier"}
        supplier={formSupplier}
        onSave={saveSupplier}
        onCancel={() => {
          setFormSupplier(undefined);
          setError("");
        }}
        saving={saving}
        error={error}
      />
    );
  }

  return (
    <div className="products-page">
      <div className="products-toolbar">
        <div>
          <h2>Supplier directory</h2>
          <p>
            Manage supplier relationships and contact information.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => {
            setError("");
            setSuccess("");
            setFormSupplier(null);
          }}
        >
          <Plus size={17} />
          Add supplier
        </button>
      </div>

      <ErrorBanner
        message={error}
        onDismiss={() => setError("")}
      />

      <SuccessBanner
        message={success}
        onDismiss={() => setSuccess("")}
      />

      <div className="product-summary-grid">
        <article className="product-summary-card">
          <span>Total suppliers</span>
          <strong>{suppliers.length}</strong>
        </article>

        <article className="product-summary-card">
          <span>Active suppliers</span>
          <strong>{activeCount}</strong>
        </article>

        <article className="product-summary-card">
          <span>Inactive suppliers</span>
          <strong>{suppliers.length - activeCount}</strong>
        </article>
      </div>

      <section className="product-table-panel">
        <div className="product-table-toolbar">
          <div>
            <h3>All suppliers</h3>
            <p>Search and manage supplier records.</p>
          </div>

          <div className="product-filters">
            <SearchField
              value={search}
              onChange={setSearch}
              placeholder="Search suppliers..."
            />

            <label className="inactive-toggle">
              <input
                type="checkbox"
                checked={showInactive}
                onChange={(event) =>
                  setShowInactive(event.target.checked)
                }
              />
              Show inactive
            </label>

            <button
              className="icon-button"
              onClick={loadSuppliers}
              disabled={loading}
              aria-label="Refresh suppliers"
            >
              <RefreshCw
                size={17}
                className={loading ? "spin" : ""}
              />
            </button>
          </div>
        </div>

        {loading ? (
          <LoadingPanel message="Loading suppliers..." />
        ) : filteredSuppliers.length === 0 ? (
          <EmptyState
            title="No suppliers found"
            description={
              search
                ? "Try another search term."
                : "Add a supplier to start your directory."
            }
            icon={Truck}
          />
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Contact person</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredSuppliers.map((supplier) => (
                  <tr key={supplier.id}>
                    <td>
                      <div className="product-name-cell">
                        <div className="product-avatar">
                          <Truck size={18} />
                        </div>

                        <div>
                          <strong>{supplier.name}</strong>
                          <span>
                            {supplier.address || "No address provided"}
                          </span>
                        </div>
                      </div>
                    </td>

                    <td>{supplier.contact_person || "—"}</td>
                    <td>{supplier.email || "—"}</td>
                    <td>{supplier.phone || "—"}</td>

                    <td>
                      <span
                        className={`product-status ${
                          supplier.is_active === false
                            ? "inactive"
                            : "active"
                        }`}
                      >
                        {supplier.is_active === false
                          ? "Inactive"
                          : "Active"}
                      </span>
                    </td>

                    <td>
                      <div className="product-actions">
                        <button
                          className="icon-button"
                          title="Edit supplier"
                          aria-label={`Edit ${supplier.name}`}
                          onClick={() => {
                            setError("");
                            setSuccess("");
                            setFormSupplier(supplier);
                          }}
                        >
                          <Pencil size={16} />
                        </button>

                        <button
                          className="icon-button danger-button"
                          title="Delete supplier"
                          aria-label={`Delete ${supplier.name}`}
                          onClick={() => deleteSupplier(supplier)}
                        >
                          <Ban size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="product-table-footer">
          Showing {filteredSuppliers.length} of {suppliers.length} suppliers
        </div>
      </section>
    </div>
  );
}

/* =========================================
   MAIN APPLICATION
========================================= */

export default function App() {
  const [dashboard, setDashboard] = useState(null);
  const [activePage, setActivePage] = useState("Dashboard");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem("mini-erp-theme") === "dark"
  );

  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode
      ? "dark"
      : "light";

    localStorage.setItem(
      "mini-erp-theme",
      darkMode ? "dark" : "light"
    );
  }, [darkMode]);

  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/dashboard/");

      setDashboard(response.data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          "Unable to load dashboard data. Check the backend connection."
        )
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const pageIcons = {
    Dashboard: LayoutDashboard,
    Products: Package,
    Inventory: Boxes,
    Suppliers: Truck,
    "Purchase Orders": ClipboardList,
    "Sales Orders": ShoppingCart,
    "AI Assistant": Bot,
  };

  const ActiveIcon = pageIcons[activePage] || LayoutDashboard;

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <button
          className="sidebar-overlay"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`sidebar ${
          sidebarOpen ? "sidebar-open" : ""
        }`}
      >
        <div className="brand">
          <div className="brand-mark">
            <Activity size={23} />
          </div>

          <div>
            <h2>Mini ERP</h2>
            <span>Business operations</span>
          </div>

          <button
            className="mobile-close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close navigation"
          >
            <X size={20} />
          </button>
        </div>

        <p className="nav-heading">WORKSPACE</p>

        <nav className="navigation">
          {navigation.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`nav-item ${
                activePage === label ? "nav-active" : ""
              }`}
              onClick={() => {
                setActivePage(label);
                setSidebarOpen(false);
              }}
            >
              <Icon size={19} />
              <span>{label}</span>

              {activePage === label && (
                <span className="active-indicator" />
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot" />

          <div>
            <strong>Backend connection</strong>
            <span>127.0.0.1:8001</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation"
          >
            <Menu size={22} />
          </button>

          <div className="breadcrumb">
            <span>Workspace</span>
            <span className="breadcrumb-divider">/</span>
            <strong>{activePage}</strong>
          </div>

          <div className="topbar-right">
            <button
              className="theme-toggle"
              onClick={() =>
                setDarkMode((current) => !current)
              }
              aria-label={
                darkMode
                  ? "Switch to light mode"
                  : "Switch to dark mode"
              }
            >
              {darkMode ? (
                <Sun size={19} />
              ) : (
                <Moon size={19} />
              )}

              <span>
                {darkMode ? "Light mode" : "Dark mode"}
              </span>
            </button>

            <span className="environment-badge">
              <span className="status-dot" />
              Development
            </span>

            <div className="avatar">S</div>
          </div>
        </header>

        <section className="page-container">
        {activePage === "Products" ? (
  <ProductsPage />
) : activePage === "Inventory" ? (
  <InventoryPage />
) : activePage === "Suppliers" ? (
  <SuppliersPage />
) : activePage === "Purchase Orders" ? (
  <PurchaseOrdersPage />
) : activePage === "Sales Orders" ? (
  <SalesOrdersPage />
) : activePage === "AI Assistant" ? (
  <AIAssistantPage />
) : (
            <>
              <div className="page-heading">
                <div>
                  <p className="eyebrow">BUSINESS OVERVIEW</p>
                  <h1>{activePage}</h1>

                  <p className="page-description">
                    {activePage === "Dashboard"
                      ? "Monitor your business operations in one place."
                      : `Your ${activePage.toLowerCase()} workspace.`}
                  </p>
                </div>

                {activePage === "Dashboard" && (
                  <button
                    className="refresh-button"
                    onClick={loadDashboard}
                    disabled={loading}
                  >
                    <RefreshCw
                      size={16}
                      className={loading ? "spin" : ""}
                    />
                    Refresh data
                  </button>
                )}
              </div>

              {activePage !== "Dashboard" ? (
                <section className="placeholder-panel">
                  <div className="placeholder-icon">
                    <ActiveIcon size={28} />
                  </div>

                  <h2>{activePage}</h2>

                  <p>
                    This module is not implemented yet. We'll
                    connect it to your existing backend next.
                  </p>

                  <button
                    className="primary-button"
                    onClick={() =>
                      setActivePage("Dashboard")
                    }
                  >
                    Return to dashboard
                  </button>
                </section>
              ) : (
                <>
                  <ErrorBanner
                    message={error}
                    onDismiss={() => setError("")}
                  />

                  <div className="section-heading">
                    <h2>Key metrics</h2>
                    <span>Live API data</span>
                  </div>

                  {loading && !dashboard ? (
                    <LoadingPanel message="Loading your business data..." />
                  ) : dashboard ? (
                    <>
                      <div className="metrics-grid">
                        <DashboardCard
                          title="Total products"
                          value={dashboard.total_products}
                          subtitle="Products in your catalog"
                          icon={Package}
                          accent="blue"
                        />

                        <DashboardCard
                          title="Inventory value"
                          value={formatCurrency(
                            dashboard.inventory_value
                          )}
                          subtitle="Current inventory valuation"
                          icon={Boxes}
                          accent="purple"
                        />

                        <DashboardCard
                          title="Sales revenue"
                          value={formatCurrency(
                            dashboard.total_sales_revenue
                          )}
                          subtitle={`${dashboard.total_sales_orders} sales orders`}
                          icon={ShoppingCart}
                          accent="green"
                        />

                        <DashboardCard
                          title="Total suppliers"
                          value={dashboard.total_suppliers}
                          subtitle="Registered suppliers"
                          icon={Users}
                          accent="orange"
                        />
                      </div>

                      <div className="section-heading second-section">
                        <h2>Operations overview</h2>
                        <span>Current status</span>
                      </div>

                      <div className="operations-grid">
                        <article className="operation-card">
                          <div className="operation-header">
                            <div className="operation-icon blue">
                              <Boxes size={20} />
                            </div>

                            <span className="status-label status-neutral">
                              Inventory
                            </span>
                          </div>

                          <p className="operation-label">
                            Units in stock
                          </p>

                          <h2>
                            {dashboard.total_inventory_units}
                          </h2>

                          <p className="operation-note">
                            Total units across inventory
                          </p>
                        </article>

                        <article className="operation-card">
                          <div className="operation-header">
                            <div className="operation-icon orange">
                              <AlertTriangle size={20} />
                            </div>

                            <span
                              className={`status-label ${
                                dashboard.low_stock_products?.length
                                  ? "status-warning"
                                  : "status-good"
                              }`}
                            >
                              {dashboard.low_stock_products?.length
                                ? "Action needed"
                                : "All clear"}
                            </span>
                          </div>

                          <p className="operation-label">
                            Low-stock products
                          </p>

                          <h2>
                            {dashboard.low_stock_products?.length ?? 0}
                          </h2>

                          <p className="operation-note">
                            Alert threshold:{" "}
                            {dashboard.low_stock_threshold} units
                          </p>
                        </article>

                        <article className="operation-card">
                          <div className="operation-header">
                            <div className="operation-icon purple">
                              <ClipboardList size={20} />
                            </div>

                            <span className="status-label status-neutral">
                              Purchasing
                            </span>
                          </div>

                          <p className="operation-label">
                            Pending purchase orders
                          </p>

                          <h2>
                            {dashboard.pending_purchase_orders}
                          </h2>

                          <p className="operation-note">
                            Orders awaiting completion
                          </p>
                        </article>
                      </div>

                      <section className="stock-panel">
                        <div className="stock-panel-heading">
                          <div>
                            <h2>Low-stock alerts</h2>
                            <p>
                              Products at or below your configured
                              threshold
                            </p>
                          </div>

                          <span className="alert-count">
                            {dashboard.low_stock_products?.length ?? 0} alerts
                          </span>
                        </div>

                        {dashboard.low_stock_products?.length ? (
                          <div className="table-wrapper">
                            <table>
                              <thead>
                                <tr>
                                  <th>Product</th>
                                  <th>SKU</th>
                                  <th>Available stock</th>
                                </tr>
                              </thead>

                              <tbody>
                                {dashboard.low_stock_products.map(
                                  (product, index) => (
                                    <tr key={product.id ?? index}>
                                      <td>
                                        {product.name ?? "Unnamed product"}
                                      </td>

                                      <td>{product.sku ?? "—"}</td>

                                      <td>
                                        {product.quantity ?? "—"}
                                      </td>
                                    </tr>
                                  )
                                )}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <EmptyState
                            title="No low-stock alerts"
                            description="No products are currently flagged by the backend."
                            icon={Boxes}
                          />
                        )}
                      </section>
                    </>
                  ) : null}

                  {lastUpdated && (
                    <p className="last-updated">
                      Last updated: {lastUpdated.toLocaleTimeString()}
                    </p>
                  )}
                </>
              )}
            </>
          )}
        </section>
      </main>
    </div>
  );
}