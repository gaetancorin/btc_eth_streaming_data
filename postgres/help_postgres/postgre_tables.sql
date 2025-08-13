DROP TABLE IF EXISTS btc_usd;
DROP TABLE IF EXISTS eth_usd;

CREATE TABLE btc_usd (
  id SERIAL PRIMARY KEY,
  price NUMERIC(15,4) NOT NULL,
  recorded_utc_at TIMESTAMPTZ(0) NOT NULL
);

CREATE TABLE eth_usd (
  id SERIAL PRIMARY KEY,
  price NUMERIC(15,4) NOT NULL,
  recorded_utc_at TIMESTAMPTZ(0) NOT NULL
);

INSERT INTO btc_usd (price, recorded_at)
VALUES
    (29500.1234, '2025-08-12 15:30:00+00'),
    (29520.5678, '2025-08-12 15:31:00+00');

INSERT INTO eth_usd (price, recorded_at)
VALUES
    (1850.5678, '2025-08-12 15:30:00+00'),
    (1852.2345, '2025-08-12 15:31:00+00');