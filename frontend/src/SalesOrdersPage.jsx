import { useEffect, useMemo, useState } from "react";
import {
  ShoppingCart,
  Plus,
  RefreshCw,
  Eye,
  ArrowLeft,
} from "lucide-react";

import api from "./services/api";

const currency = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(Number(value ?? 0));

const formatDate = (value) => {
  if (!value) return "—";

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short",
      });
};

function getErrorMessage(error, fallback) {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(", ");
  }

  return fallback;
}

function StatusBadge({ status }) {
  const value = String(status || "unknown");

  const completed =
    value.toLowerCase().includes("complete") ||
    value.toLowerCase().includes("delivered");

  return (
    <span
      className={`product-status ${completed ? "active" : "inactive"}`}
    >
      {value.replaceAll("_", " ")}
    </span>
  );
}

function SalesOrderForm({ products, onCancel, onCreated }) {
  const [customerName, setCustomerName] = useState("");
  const [items, setItems] = useState([
    { product_id: "", quantity: "1" },
  ]);

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  function updateItem(index, field, value) {
    setItems((current) =>
      current.map((item, itemIndex) =>
        itemIndex === index
          ? { ...item, [field]: value }
          : item
      )
    );
  }

  function addItem() {
    setItems((current) => [
      ...current,
      { product_id: "", quantity: "1" },
    ]);
  }

  function removeItem(index) {
    setItems((current) =>
      current.filter((_, itemIndex) => itemIndex !== index)
    );
  }

  const estimatedTotal = useMemo(
    () =>
      items.reduce((sum, item) => {
        const product = products.find(
          (candidate) => candidate.id === Number(item.product_id)
        );

        return (
          sum +
          Number(product?.price ?? 0) *
            Math.max(0, Number(item.quantity) || 0)
        );
      }, 0),
    [items, products]
  );

  async function submit(event) {
    event.preventDefault();
    setError("");

    const name = customerName.trim();

    if (!name) {
      setError("Enter the customer's name.");
      return;
    }

    if (name.length > 200) {
      setError("Customer name must be 200 characters or fewer.");
      return;
    }

    if (items.length === 0) {
      setError("Add at least one product.");
      return;
    }

    const payloadItems = [];

    for (const item of items) {
      const productId = Number(item.product_id);
      const quantity = Number(item.quantity);

      if (!Number.isInteger(productId) || productId <= 0) {
        setError("Select a valid product for every order item.");
        return;
      }

      if (!Number.isInteger(quantity) || quantity <= 0) {
        setError("Quantities must be positive whole numbers.");
        return;
      }

      payloadItems.push({
        product_id: productId,
        quantity,
      });
    }

    setSaving(true);

    try {
      await api.post("/sales-orders/", {
        customer_name: name,
        items: payloadItems,
      });

      await onCreated();
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to create sales order.")
      );
    } finally {
      setSaving(false);
    }
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
          Back to sales orders
        </button>

        <h2>Create sales order</h2>

        <p>
          Enter the customer details and select the products being sold.
        </p>
      </div>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

      <form className="product-form" onSubmit={submit}>
        <label className="full-width">
          Customer name <span>*</span>

          <input
            value={customerName}
            onChange={(event) => setCustomerName(event.target.value)}
            maxLength={200}
            placeholder="Enter customer or company name"
            required
          />
        </label>

        <div className="full-width">
          <div className="products-toolbar">
            <div>
              <h3>Products</h3>
              <p>Select products and enter quantities.</p>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={addItem}
              disabled={saving || products.length === 0}
            >
              <Plus size={16} />
              Add product
            </button>
          </div>

          {items.map((item, index) => {
            const selectedProduct = products.find(
              (product) => product.id === Number(item.product_id)
            );

            return (
              <div
                key={index}
                className="sales-order-item"
                style={{
                  display: "grid",
                  gridTemplateColumns: "minmax(180px, 2fr) 1fr auto",
                  gap: "12px",
                  alignItems: "end",
                  marginBottom: "16px",
                }}
              >
                <label>
                  Product <span>*</span>

                  <select
                    value={item.product_id}
                    onChange={(event) =>
                      updateItem(index, "product_id", event.target.value)
                    }
                    required
                  >
                    <option value="">Select product</option>

                    {products
                      .filter((product) => product.is_active !== false)
                      .map((product) => (
                        <option key={product.id} value={product.id}>
                          {product.name} — {product.sku}
                        </option>
                      ))}
                  </select>

                  {selectedProduct && (
                    <small>
                      Price: {currency(selectedProduct.price)} per unit
                      {" · "}Available: {selectedProduct.quantity}
                    </small>
                  )}
                </label>

                <label>
                  Quantity <span>*</span>

                  <input
                    type="number"
                    min="1"
                    step="1"
                    value={item.quantity}
                    onChange={(event) =>
                      updateItem(index, "quantity", event.target.value)
                    }
                    required
                  />
                </label>

                <button
                  type="button"
                  className="icon-button danger-button"
                  title="Remove product"
                  aria-label={`Remove product ${index + 1}`}
                  onClick={() => removeItem(index)}
                  disabled={saving || items.length === 1}
                >
                  ×
                </button>
              </div>
            );
          })}
        </div>

        <div className="full-width purchase-order-total">
          <span>Estimated total</span>
          <strong>{currency(estimatedTotal)}</strong>
          <small>
            The backend determines the final order amount using its pricing
            rules.
          </small>
        </div>

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
            disabled={saving || products.length === 0}
          >
            {saving ? "Creating..." : "Create sales order"}
          </button>
        </div>
      </form>
    </section>
  );
}

function SalesOrderDetails({ order, products, onBack }) {
  const productName = (productId) => {
    const product = products.find(
      (candidate) => candidate.id === productId
    );

    return product
      ? `${product.name} (${product.sku})`
      : `Product #${productId}`;
  };

  return (
    <section className="product-table-panel">
      <div className="product-table-toolbar">
        <div>
          <button className="back-button" onClick={onBack}>
            <ArrowLeft size={17} />
            Back to sales orders
          </button>

          <h2>Sales Order #{order.id}</h2>
          <p>Created {formatDate(order.created_at)}</p>
        </div>

        <StatusBadge status={order.status} />
      </div>

      <div className="product-summary-grid">
        <article className="product-summary-card">
          <span>Customer</span>
          <strong>{order.customer_name}</strong>
        </article>

        <article className="product-summary-card">
          <span>Order total</span>
          <strong>{currency(order.total_amount)}</strong>
        </article>

        <article className="product-summary-card">
          <span>Product lines</span>
          <strong>{order.items?.length ?? 0}</strong>
        </article>
      </div>

      <h3>Order items</h3>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Product</th>
              <th>Quantity</th>
              <th>Unit price</th>
              <th>Line total</th>
            </tr>
          </thead>

          <tbody>
            {(order.items || []).map((item) => (
              <tr key={item.id}>
                <td>{productName(item.product_id)}</td>
                <td>{item.quantity}</td>
                <td>{currency(item.unit_price)}</td>
                <td>{currency(item.line_total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default function SalesOrdersPage() {
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [search, setSearch] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");

    try {
      const [ordersResponse, productsResponse] = await Promise.all([
        api.get("/sales-orders/"),
        api.get("/products/"),
      ]);

      if (
        !Array.isArray(ordersResponse.data) ||
        !Array.isArray(productsResponse.data)
      ) {
        throw new Error("The backend returned an unexpected response.");
      }

      setOrders(ordersResponse.data);
      setProducts(productsResponse.data);
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to load sales order information.")
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function viewOrder(orderId) {
    setError("");
    setSuccess("");

    try {
      const response = await api.get(`/sales-orders/${orderId}`);
      setSelectedOrder(response.data);
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to load sales order details.")
      );
    }
  }

  async function orderCreated() {
    setShowForm(false);
    setSelectedOrder(null);
    setSuccess("Sales order created successfully.");
    await loadData();
  }

  const filteredOrders = orders.filter((order) => {
    const query = search.trim().toLowerCase();

    return (
      String(order.id).includes(query) ||
      String(order.customer_name).toLowerCase().includes(query) ||
      String(order.status).toLowerCase().includes(query)
    );
  });

  const totalRevenue = orders.reduce(
    (sum, order) => sum + Number(order.total_amount || 0),
    0
  );

  if (showForm) {
    return (
      <SalesOrderForm
        products={products}
        onCancel={() => setShowForm(false)}
        onCreated={orderCreated}
      />
    );
  }

  if (selectedOrder) {
    return (
      <SalesOrderDetails
        order={selectedOrder}
        products={products}
        onBack={() => {
          setSelectedOrder(null);
          setSuccess("");
        }}
      />
    );
  }

  return (
    <div className="products-page">
      <div className="products-toolbar">
        <div>
          <h2>Sales Orders</h2>
          <p>Manage customer orders and track sales revenue.</p>
        </div>

        <button
          className="primary-button"
          onClick={() => {
            setError("");
            setSuccess("");
            setShowForm(true);
          }}
        >
          <Plus size={17} />
          Create sales order
        </button>
      </div>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

      {success && (
        <div className="success-banner" role="status">
          {success}
        </div>
      )}

      <div className="product-summary-grid">
        <article className="product-summary-card">
          <span>Total sales orders</span>
          <strong>{orders.length}</strong>
        </article>

        <article className="product-summary-card">
          <span>Total order value</span>
          <strong>{currency(totalRevenue)}</strong>
        </article>

        <article className="product-summary-card">
          <span>Products in catalog</span>
          <strong>
            {products.filter((product) => product.is_active !== false).length}
          </strong>
        </article>
      </div>

      <section className="product-table-panel">
        <div className="product-table-toolbar">
          <div>
            <h3>Sales history</h3>
            <p>Search orders and inspect their details.</p>
          </div>

          <div className="product-filters">
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search customer or order..."
              aria-label="Search sales orders"
            />

            <button
              className="icon-button"
              onClick={loadData}
              disabled={loading}
              aria-label="Refresh sales orders"
            >
              <RefreshCw
                size={17}
                className={loading ? "spin" : ""}
              />
            </button>
          </div>
        </div>

        {loading ? (
          <p>Loading sales orders...</p>
        ) : filteredOrders.length === 0 ? (
          <div className="empty-state">
            <ShoppingCart size={30} />
            <h3>No sales orders found</h3>
            <p>Create a sales order to get started.</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer</th>
                  <th>Created</th>
                  <th>Items</th>
                  <th>Total amount</th>
                  <th>Status</th>
                  <th>Details</th>
                </tr>
              </thead>

              <tbody>
                {filteredOrders.map((order) => (
                  <tr key={order.id}>
                    <td>SO-{String(order.id).padStart(4, "0")}</td>
                    <td>{order.customer_name}</td>
                    <td>{formatDate(order.created_at)}</td>
                    <td>{order.items?.length ?? 0}</td>
                    <td>{currency(order.total_amount)}</td>
                    <td>
                      <StatusBadge status={order.status} />
                    </td>
                    <td>
                      <button
                        className="icon-button"
                        title="View sales order"
                        aria-label={`View sales order ${order.id}`}
                        onClick={() => viewOrder(order.id)}
                      >
                        <Eye size={17} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="product-table-footer">
          Showing {filteredOrders.length} of {orders.length} sales orders
        </div>
      </section>
    </div>
  );
}