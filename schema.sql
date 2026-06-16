-- Schema for Package Return Tracker

CREATE TABLE Orders (
  order_id TEXT PRIMARY KEY,
  vendor TEXT,
  item TEXT,
  category TEXT,
  price REAL,
  order_date TEXT,
  delivery_date TEXT,
  status TEXT
);

CREATE TABLE Return_Windows (
  window_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id TEXT,
  return_by_date TEXT,
  days_left INTEGER,
  FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);

CREATE TABLE Return_Reasons (
  reason_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id TEXT,
  reason_text TEXT,
  reason_category TEXT,
  FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);

CREATE TABLE Notifications (
  notif_id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id TEXT,
  message TEXT,
  created_date TEXT,
  is_read INTEGER DEFAULT 0,
  FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);

