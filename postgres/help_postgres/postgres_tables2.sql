DROP TABLE IF EXISTS btc_eth_gap_avg_3m_indicator;
DROP TABLE IF EXISTS btc_eth_gap_avg_5m_indicator;
DROP TABLE IF EXISTS btc_usd_avg_indicator;
DROP TABLE IF EXISTS eth_usd_avg_indicator;
DROP TABLE IF EXISTS btc_usd;
DROP TABLE IF EXISTS eth_usd;

CREATE TABLE btc_usd (
  id SERIAL PRIMARY KEY,
  price NUMERIC(15,4) NOT NULL,
  datetime_utc TIMESTAMPTZ(0) NOT NULL UNIQUE
);

CREATE TABLE eth_usd (
  id SERIAL PRIMARY KEY,
  price NUMERIC(15,4) NOT NULL,
  datetime_utc TIMESTAMPTZ(0) NOT NULL UNIQUE
);

CREATE TABLE btc_usd_avg_indicator (
    id SERIAL PRIMARY KEY,
    btc_usd_id INT NOT NULL REFERENCES btc_usd(id) ON DELETE CASCADE,
    price_avg_3m NUMERIC(15,4) NOT NULL,
    price_avg_5m NUMERIC(15,4),
    datetime_utc TIMESTAMPTZ(0) NOT NULL UNIQUE
);

CREATE TABLE eth_usd_avg_indicator (
    id SERIAL PRIMARY KEY,
    eth_usd_id INT NOT NULL REFERENCES eth_usd(id) ON DELETE CASCADE,
    price_avg_3m NUMERIC(15,4) NOT NULL,
    price_avg_5m NUMERIC(15,4),
    datetime_utc TIMESTAMPTZ(0) NOT NULL UNIQUE
);

CREATE TABLE btc_eth_gap_avg_5m_indicator (
    id SERIAL PRIMARY KEY,
    btc_eth_gap_avg_5m NUMERIC(15,4),
    datetime_utc TIMESTAMPTZ(0) NOT NULL UNIQUE
);

CREATE TABLE btc_eth_gap_avg_3m_indicator (
    id SERIAL PRIMARY KEY,
    btc_eth_gap_avg_3m NUMERIC(15,4),
    datetime_utc TIMESTAMPTZ(0) NOT NULL UNIQUE
);

INSERT INTO btc_usd (price, recorded_at)
VALUES
    (129500.1234, '2025-08-12 15:30:00+00'),
    (129520.5678, '2025-08-12 15:31:00+00');
    (129524.9678, '2025-08-12 15:32:00+00');
    (129528.7418, '2025-08-12 15:33:00+00');
    (129585.4278, '2025-08-12 15:34:00+00');
    (129599.4878, '2025-08-12 15:35:00+00');

INSERT INTO eth_usd (price, recorded_at)
VALUES
    (1850.5678, '2025-08-12 15:30:00+00'),
    (1845.4845, '2025-08-12 15:31:00+00');
    (1815.6245, '2025-08-12 15:32:00+00');
    (1845.8145, '2025-08-12 15:33:00+00');
    (1845.2484, '2025-08-12 15:34:00+00');
    (1848.9782, '2025-08-12 15:35:00+00');

INSERT INTO btc_usd_avg_indicator (btc_usd_id, price_avg_3m, price_avg_5m, datetime_utc)
VALUES
    (1, 116689.0100, 116605.4828, '2025-08-12 15:30:00+00'),
    (2, 116635.7280, 116576.8388, '2025-08-12 15:31:00+00'),
    (3, 116546.6313, 116572.0448, '2025-08-12 15:32:00+00');

INSERT INTO btc_usd_avg_indicator (btc_usd_id, price_avg_3m, price_avg_5m, datetime_utc)
VALUES
    (1, 4689.0100, 4605.4828, '2025-08-12 15:30:00+00'),
    (2, 4635.7280, 4576.8388, '2025-08-12 15:31:00+00'),
    (3, 4546.6313, 4572.0448, '2025-08-12 15:32:00+00');

INSERT INTO btc_eth_gap_avg_5m_indicator (btc_eth_gap_avg_5m, datetime_utc)
VALUES
    (94578.9450, '2025-08-12 15:30:00+00'),
    (95875.9850, '2025-08-12 15:31:00+00'),
    (92545.9920, '2025-08-12 15:32:00+00'),
    (954657.0100, '2025-08-12 15:33:00+00'),