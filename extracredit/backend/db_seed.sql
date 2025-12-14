DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer TEXT NOT NULL,
    status TEXT NOT NULL,
    total REAL NOT NULL,
    city TEXT NOT NULL,
    channel TEXT NOT NULL,
    created_at TEXT NOT NULL
);

INSERT INTO orders (order_id, customer, status, total, city, channel, created_at) VALUES
    (101, 'Acme Co', 'delivered', 1250.40, 'New York', 'web', '2024-10-02'),
    (102, 'Bright Future', 'pending', 980.00, 'Chicago', 'mobile', '2024-10-05'),
    (103, 'Acme Co', 'processing', 430.75, 'New York', 'web', '2024-10-09'),
    (104, 'Helios Labs', 'delivered', 2100.99, 'San Francisco', 'sales', '2024-09-15'),
    (105, 'Bright Future', 'cancelled', 150.00, 'Chicago', 'web', '2024-10-11'),
    (106, 'Nexus Retail', 'delivered', 780.50, 'Austin', 'mobile', '2024-10-03'),
    (107, 'Summit Foods', 'pending', 340.10, 'Denver', 'web', '2024-10-08'),
    (108, 'Helios Labs', 'processing', 665.45, 'San Francisco', 'mobile', '2024-10-10'),
    (109, 'Greenline', 'delivered', 320.20, 'Boston', 'web', '2024-09-28'),
    (110, 'FutureVision', 'pending', 1430.85, 'Seattle', 'mobile', '2024-10-04'),
    (111, 'Acme Co', 'delivered', 880.10, 'New York', 'sales', '2024-10-07'),
    (112, 'Bright Future', 'processing', 260.00, 'Chicago', 'web', '2024-10-09');
