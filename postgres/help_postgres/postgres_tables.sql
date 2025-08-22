DROP TABLE IF EXISTS btc_usd_avg_indicator;
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

INSERT INTO btc_usd (price, recorded_at)
VALUES
    (29500.1234, '2025-08-12 15:30:00+00'),
    (29520.5678, '2025-08-12 15:31:00+00');
    (29520.9678, '2025-08-12 15:32:00+00');

INSERT INTO eth_usd (price, recorded_at)
VALUES
    (1850.5678, '2025-08-12 15:30:00+00'),
    (1852.2345, '2025-08-12 15:31:00+00');

INSERT INTO btc_usd_avg_indicator (btc_usd_id, price_avg_3m, price_avg_5m, datetime_utc)
VALUES
    (1, 116689.0100, 116605.4828, '2025-08-12 15:30:00+00'),
    (2, 116635.7280, 116576.8388, '2025-08-12 15:31:00+00'),
    (3, 116546.6313, 116572.0448, '2025-08-12 15:32:00+00');