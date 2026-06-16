-- Seed data (15 orders)

-- Notes:
-- status values are strings (e.g., 'delivered_no_decision', 'kept', 'return_in_progress', 'returned').

INSERT INTO Orders (order_id, vendor, item, category, price, order_date, delivery_date, status) VALUES
('ORD-SEED-001', 'Amazon', 'Denim jacket', 'clothing', 74.99, '2025-01-01', '2025-01-07', 'kept'),
('ORD-SEED-002', 'BestBuy', 'Wireless earbuds', 'electronics', 129.99, '2025-01-02', '2025-01-06', 'returned'),
('ORD-SEED-003', 'Target', 'Cotton T-shirt', 'clothing', 19.99, '2025-01-03', '2025-01-08', 'return_in_progress'),
('ORD-SEED-004', 'Walmart', 'Air purifier', 'home', 189.50, '2025-01-04', '2025-01-09', 'delivered_no_decision'),

-- Edge case: return window closing tomorrow
('ORD-SEED-005', 'IKEA', 'Desk lamp', 'home', 39.95, '2025-01-01', '2025-01-09', 'delivered_no_decision'),

-- Edge case: delivered today with no decision
('ORD-SEED-006', 'Newegg', 'Smart watch', 'electronics', 149.00, '2025-01-12', '2025-01-13', 'delivered_no_decision'),

-- Edge case: already kept
('ORD-SEED-007', 'Etsy', 'Casual hoodie', 'clothing', 45.00, '2025-01-05', '2025-01-10', 'kept'),

-- Edge case: mid-return in progress
('ORD-SEED-008', 'Kobo', 'Business strategy book', 'books', 22.50, '2025-01-04', '2025-01-08', 'return_in_progress'),

-- Varied remaining
('ORD-SEED-009', 'Zappos', 'Leather sneakers', 'shoes', 88.10, '2025-01-02', '2025-01-07', 'returned'),
('ORD-SEED-010', 'Amazon', 'Noise cancelling headphones', 'electronics', 199.99, '2025-01-06', '2025-01-10', 'returned'),
('ORD-SEED-011', 'Target', 'Science textbook', 'books', 31.25, '2025-01-03', '2025-01-08', 'delivered_no_decision'),
('ORD-SEED-012', 'BestBuy', 'Bluetooth speaker', 'electronics', 59.99, '2025-01-05', '2025-01-09', 'kept'),
('ORD-SEED-013', 'Walmart', 'Vacuum cleaner', 'home', 129.00, '2025-01-06', '2025-01-10', 'return_in_progress'),
('ORD-SEED-014', 'Etsy', 'Sweater', 'clothing', 54.99, '2025-01-06', '2025-01-11', 'returned'),
('ORD-SEED-015', 'IKEA', 'Storage organizer set', 'home', 24.99, '2025-01-07', '2025-01-12', 'delivered_no_decision');

-- Return windows: assume 14-day return window
-- days_left is computed relative to '2025-01-13' (the assumed "today" in seed script).

INSERT INTO Return_Windows (order_id, return_by_date, days_left) VALUES
('ORD-SEED-001', '2025-01-21', 8),
('ORD-SEED-002', '2025-01-20', 7),
('ORD-SEED-003', '2025-01-22', 9),
('ORD-SEED-004', '2025-01-23', 10),

('ORD-SEED-005', '2025-01-14', 1),

('ORD-SEED-006', '2025-01-27', 14),

('ORD-SEED-007', '2025-01-24', 11),

('ORD-SEED-008', '2025-01-22', 9),

('ORD-SEED-009', '2025-01-21', 8),
('ORD-SEED-010', '2025-01-24', 11),
('ORD-SEED-011', '2025-01-22', 9),
('ORD-SEED-012', '2025-01-23', 10),
('ORD-SEED-013', '2025-01-24', 11),
('ORD-SEED-014', '2025-01-25', 12),
('ORD-SEED-015', '2025-01-26', 13);

-- Return reasons (only for returned or in-progress orders)

INSERT INTO Return_Reasons (order_id, reason_text, reason_category) VALUES
('ORD-SEED-002', 'Arrived broken, box was crushed', 'damaged'),
('ORD-SEED-003', 'Runs small for me, doesn’t fit', 'size_issue'),
('ORD-SEED-005', 'Not using it anymore', 'changed_mind'),
('ORD-SEED-008', 'Expected it to be different than the listing', 'not_as_described'),
('ORD-SEED-009', 'Shoes too narrow, hurt after an hour', 'size_issue'),
('ORD-SEED-010', 'Didn’t match the photos—quality was off', 'not_as_described'),
('ORD-SEED-013', 'Too expensive for what it is', 'price'),
('ORD-SEED-014', 'Didn’t fit and sizing feels inconsistent', 'size_issue');

-- Notifications (some seeded)

INSERT INTO Notifications (order_id, message, created_date, is_read) VALUES
('ORD-SEED-005', 'Return window closing tomorrow. Please confirm whether to return.', '2025-01-13', 0),
('ORD-SEED-004', 'Reminder: your return window is open. Decision due soon.', '2025-01-12', 1),
('ORD-SEED-013', 'Heads up: return is in progress—track shipping status.', '2025-01-11', 0); 

