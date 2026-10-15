import { useEffect, useMemo, useState } from "react";
import {
  ClipboardList,
  Plus,
  RefreshCw,
  Eye,
  PackageCheck,
  ArrowLeft,
  X,
} from "lucide-react";

import api from "./services/api";

const currency = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(Number(value ?? 0));

const dateFormat = (value) => {
  if (!value) return "—";

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short",
      });
};

function errorMessage(error, fallback) {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(", ");
  }

  return fallback;
}

function OrderStatus({ status }) {
  const value = String(status || "unknown");

  return (
    <span
      className={`product-status ${
        value.toLowerCase().includes("complete") ||
        value.toLowerCase().includes("received")
          ? "active"
          : "inactive"
      }`}
    >
      {value.replaceAll("_", " ")}
    </span>
  );
}

function PurchaseOrderForm({
  suppliers,
  products,
  onCancel,
  onCreated,
}) {
  const [supplierId, setSupplierId] = useState("");
  const [items, setItems] = useState([
    { product_id: "", quantity_ordered: "1", unit_cost: "" },
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
      {
        product_id: "",
        quantity_ordered: "1",
        unit_cost: "",
      },
    ]);
  }

  function removeItem(index) {
    setItems((current) =>
      current.filter((_, itemIndex) => itemIndex !== index)
    );
  }

  const total = useMemo(
    () =>
      items.reduce(
        (sum, item) =>
          sum +
          Math.max(0, Number(item.quantity_ordered) || 0) *
            Math.max(0, Number(item.unit_cost) || 0),
        0
      ),
    [items]
  );

  async function submit(event) {
    event.preventDefault();
    setError("");

    if (!supplierId) {
      setError("Select a supplier.");
      return;
    }

    if (!items.length) {
      setError("Add at least one product.");
      return;
    }

    const payloadItems = [];

    for (const item of items) {
      const productId = Number(item.product_id);
      const quantity = Number(item.quantity_ordered);
      const unitCost = Number(item.unit_cost);

      if (!productId || !Number.isInteger(productId)) {
        setError("Select a valid product for every order item.");
        return;
      }

      if (!Number.isInteger(quantity) || quantity <= 0) {
        setError("Ordered quantities must be positive whole numbers.");
        return;
      }

      if (!Number.isFinite(unitCost) || unitCost < 0) {
        setError("Unit costs must be zero or greater.");
        return;
      }

      payloadItems.push({
        product_id: productId,
        quantity_ordered: quantity,
        unit_cost: unitCost,
      });
    }

    setSaving(true);

    try {
      await api.post("/purchase-orders/", {
        supplier_id: Number(supplierId),
        items: payloadItems,
      });

      await onCreated();
    } catch (err) {
      setError(
        errorMessage(err, "Unable to create purchase order.")
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
          Back to purchase orders
        </button>

        <h2>Create purchase order</h2>

        <p>
          Select a supplier and add the products you want to order.
        </p>
      </div>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

      <form className="product-form" onSubmit={submit}>
        <label className="full-width">
          Supplier <span>*</span>

          <select
            value={supplierId}
            onChange={(event) => setSupplierId(event.target.value)}
            required
          >
            <option value="">Select supplier</option>

            {suppliers
              .filter((supplier) => supplier.is_active !== false)
              .map((supplier) => (
                <option key={supplier.id} value={supplier.id}>
                  {supplier.name} (#{supplier.id})
                </option>
              ))}
          </select>
        </label>

        <div className="full-width">
          <div className="products-toolbar">
            <div>
              <h3>Order items</h3>
              <p>Add products, quantities, and unit costs.</p>
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

          {items.map((item, index) => (
            <div
              key={index}
              className="purchase-order-item"
              style={{
                display: "grid",
                gridTemplateColumns: "minmax(180px, 2fr) 1fr 1fr auto",
                gap: "12px",
                alignItems: "end",
                marginBottom: "16px",
              }}
            >
              <label>
                Product <span>*</span>

                <select
                  value={item.product_id}
                  onChange={(event) => {
                    const value = event.target.value;
                    updateItem(index, "product_id", value);

                    const selectedProduct = products.find(
                      (product) => product.id === Number(value)
                    );

                    if (selectedProduct) {
                      updateItem(
                        index,
                        "unit_cost",
                        String(selectedProduct.price ?? 0)
                      );
                    }
                  }}
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
              </label>

              <label>
                Quantity <span>*</span>

                <input
                  type="number"
                  min="1"
                  step="1"
                  value={item.quantity_ordered}
                  onChange={(event) =>
                    updateItem(
                      index,
                      "quantity_ordered",
                      event.target.value
                    )
                  }
                  required
                />
              </label>

              <label>
                Unit cost (₹) <span>*</span>

                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={item.unit_cost}
                  onChange={(event) =>
                    updateItem(index, "unit_cost", event.target.value)
                  }
                  required
                />
              </label>

              <button
                type="button"
                className="icon-button danger-button"
                title="Remove item"
                aria-label={`Remove order item ${index + 1}`}
                onClick={() => removeItem(index)}
                disabled={saving || items.length === 1}
              >
                <X size={17} />
              </button>
            </div>
          ))}
        </div>

        <div className="full-width">
          <div className="purchase-order-total">
            <span>Estimated order total</span>
            <strong>{currency(total)}</strong>
          </div>
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
            {saving ? "Creating..." : "Create purchase order"}
          </button>
        </div>
      </form>
    </section>
  );
}

function PurchaseOrderDetails({
  order,
  products,
  onBack,
  onReceived,
}) {
  const [receiving, setReceiving] = useState(false);
  const [quantities, setQuantities] = useState({});
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const remainingItems = (order.items || []).filter(
    (item) =>
      Number(item.quantity_ordered) >
      Number(item.quantity_received)
  );

  const productName = (productId) => {
    const product = products.find(
      (productItem) => productItem.id === productId
    );

    return product
      ? `${product.name} (${product.sku})`
      : `Product #${productId}`;
  };

  async function receiveGoods(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const receiptItems = [];

    for (const item of remainingItems) {
      const quantity = Number(quantities[item.product_id] ?? 0);

      if (!Number.isInteger(quantity) || quantity < 0) {
        setError("Received quantities must be whole numbers of zero or greater.");
        return;
      }

      const remaining =
        Number(item.quantity_ordered) -
        Number(item.quantity_received);

      if (quantity > remaining) {
        setError(
          `${productName(item.product_id)} has only ${remaining} units remaining.`
        );
        return;
      }

      if (quantity > 0) {
        receiptItems.push({
          product_id: item.product_id,
          quantity_received: quantity,
        });
      }
    }

    if (!receiptItems.length) {
      setError("Enter at least one quantity greater than zero.");
      return;
    }

    setReceiving(true);

    try {
      const response = await api.post(
        `/purchase-orders/${order.id}/receive`,
        { items: receiptItems }
      );

      setSuccess("Goods receipt recorded successfully.");
      await onReceived(response.data);
    } catch (err) {
      setError(
        errorMessage(err, "Unable to record received goods.")
      );
    } finally {
      setReceiving(false);
    }
  }

  return (
    <section className="product-table-panel">
      <div className="product-table-toolbar">
        <div>
          <button className="back-button" onClick={onBack}>
            <ArrowLeft size={17} />
            Back to orders
          </button>

          <h2>Purchase Order #{order.id}</h2>
          <p>Created {dateFormat(order.created_at)}</p>
        </div>

        <OrderStatus status={order.status} />
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
          <span>Supplier ID</span>
          <strong>#{order.supplier_id}</strong>
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

      <h3>Ordered products</h3>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Product</th>
              <th>Ordered</th>
              <th>Received</th>
              <th>Remaining</th>
              <th>Unit cost</th>
              <th>Line total</th>
            </tr>
          </thead>

          <tbody>
            {(order.items || []).map((item) => (
              <tr key={item.id}>
                <td>{productName(item.product_id)}</td>
                <td>{item.quantity_ordered}</td>
                <td>{item.quantity_received}</td>
                <td>
                  {Math.max(
                    0,
                    item.quantity_ordered - item.quantity_received
                  )}
                </td>
                <td>{currency(item.unit_cost)}</td>
                <td>{currency(item.line_total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {remainingItems.length > 0 && (
        <form className="product-form" onSubmit={receiveGoods}>
          <div className="form-heading">
            <h3>Receive goods</h3>
            <p>
              Enter the quantities received in this delivery.
              Leave items at zero if they were not delivered.
            </p>
          </div>

          {remainingItems.map((item) => {
            const remaining =
              item.quantity_ordered - item.quantity_received;

            return (
              <label key={item.product_id}>
                {productName(item.product_id)}
                <span> — up to {remaining} remaining</span>

                <input
                  type="number"
                  min="0"
                  max={remaining}
                  step="1"
                  value={quantities[item.product_id] ?? ""}
                  onChange={(event) =>
                    setQuantities((current) => ({
                      ...current,
                      [item.product_id]: event.target.value,
                    }))
                  }
                  placeholder="Quantity received"
                />
              </label>
            );
          })}

          <div className="form-actions full-width">
            <button
              type="submit"
              className="primary-button"
              disabled={receiving}
            >
              <PackageCheck size={17} />
              {receiving ? "Recording..." : "Record goods receipt"}
            </button>
          </div>
        </form>
      )}
    </section>
  );
}

export default function PurchaseOrdersPage() {
  const [orders, setOrders] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
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
      const [ordersResponse, suppliersResponse, productsResponse] =
        await Promise.all([
          api.get("/purchase-orders/"),
          api.get("/suppliers/"),
          api.get("/products/"),
        ]);

      if (
        !Array.isArray(ordersResponse.data) ||
        !Array.isArray(suppliersResponse.data) ||
        !Array.isArray(productsResponse.data)
      ) {
        throw new Error("The backend returned an unexpected response.");
      }

      setOrders(ordersResponse.data);
      setSuppliers(suppliersResponse.data);
      setProducts(productsResponse.data);
    } catch (err) {
      setError(
        errorMessage(err, "Unable to load purchase order information.")
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
      const response = await api.get(
        `/purchase-orders/${orderId}`
      );

      setSelectedOrder(response.data);
      setShowForm(false);
    } catch (err) {
      setError(
        errorMessage(err, "Unable to load purchase order details.")
      );
    }
  }

  async function orderCreated() {
    setShowForm(false);
    setSuccess("Purchase order created successfully.");
    setSelectedOrder(null);
    await loadData();
  }

  async function receiptCompleted(updatedOrder) {
    setSelectedOrder(updatedOrder);
    setSuccess("Goods receipt recorded successfully.");
    await loadData();
  }

  const filteredOrders = orders.filter((order) => {
    const query = search.trim().toLowerCase();

    return (
      String(order.id).includes(query) ||
      String(order.supplier_id).includes(query) ||
      String(order.status).toLowerCase().includes(query)
    );
  });

  const pendingCount = orders.filter(
    (order) =>
      !String(order.status).toLowerCase().includes("complete") &&
      !String(order.status).toLowerCase().includes("received")
  ).length;

  if (showForm) {
    return (
      <PurchaseOrderForm
        suppliers={suppliers}
        products={products}
        onCancel={() => setShowForm(false)}
        onCreated={orderCreated}
      />
    );
  }

  if (selectedOrder) {
    return (
      <PurchaseOrderDetails
        order={selectedOrder}
        products={products}
        onBack={() => {
          setSelectedOrder(null);
          setSuccess("");
        }}
        onReceived={receiptCompleted}
      />
    );
  }

  return (
    <div className="products-page">
      <div className="products-toolbar">
        <div>
          <h2>Purchase Orders</h2>
          <p>
            Manage supplier orders and record incoming inventory.
          </p>
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
          Create purchase order
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
          <span>Total purchase orders</span>
          <strong>{orders.length}</strong>
        </article>

        <article className="product-summary-card">
          <span>Pending orders</span>
          <strong>{pendingCount}</strong>
        </article>

        <article className="product-summary-card">
          <span>Total order value</span>
          <strong>
            {currency(
              orders.reduce(
                (sum, order) => sum + Number(order.total_amount || 0),
                0
              )
            )}
          </strong>
        </article>
      </div>

      <section className="product-table-panel">
        <div className="product-table-toolbar">
          <div>
            <h3>Order history</h3>
            <p>Review existing purchase orders and their status.</p>
          </div>

          <div className="product-filters">
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search order, supplier ID, or status..."
              aria-label="Search purchase orders"
            />

            <button
              className="icon-button"
              onClick={loadData}
              disabled={loading}
              aria-label="Refresh purchase orders"
            >
              <RefreshCw
                size={17}
                className={loading ? "spin" : ""}
              />
            </button>
          </div>
        </div>

        {loading ? (
          <p>Loading purchase orders...</p>
        ) : filteredOrders.length === 0 ? (
          <div className="empty-state">
            <ClipboardList size={30} />
            <h3>No purchase orders found</h3>
            <p>Create a purchase order to get started.</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Supplier ID</th>
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
                    <td>PO-{String(order.id).padStart(4, "0")}</td>
                    <td>#{order.supplier_id}</td>
                    <td>{dateFormat(order.created_at)}</td>
                    <td>{order.items?.length ?? 0}</td>
                    <td>{currency(order.total_amount)}</td>
                    <td>
                      <OrderStatus status={order.status} />
                    </td>
                    <td>
                      <button
                        className="icon-button"
                        title="View purchase order"
                        aria-label={`View purchase order ${order.id}`}
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
          Showing {filteredOrders.length} of {orders.length} purchase orders
        </div>
      </section>
    </div>
  );
}