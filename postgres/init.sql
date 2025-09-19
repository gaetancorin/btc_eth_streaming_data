CREATE TABLE IF NOT EXISTS btc_usd (
  id SERIAL PRIMARY KEY,
  price NUMERIC(15,4) NOT NULL,
  datetime_utc TIMESTAMPTZ(0) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS eth_usd (
  id SERIAL PRIMARY KEY,
  price NUMERIC(15,4) NOT NULL,
  datetime_utc TIMESTAMPTZ(0) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS btc_usd_avg_indicator (
    id SERIAL PRIMARY KEY,
    btc_usd_id INT NOT NULL REFERENCES btc_usd(id) ON DELETE CASCADE,
    price_avg_3m NUMERIC(15,4) NOT NULL,
    price_avg_5m NUMERIC(15,4),
    datetime_utc TIMESTAMPTZ(0) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS eth_usd_avg_indicator (
    id SERIAL PRIMARY KEY,
    eth_usd_id INT NOT NULL REFERENCES eth_usd(id) ON DELETE CASCADE,
    price_avg_3m NUMERIC(15,4) NOT NULL,
    price_avg_5m NUMERIC(15,4),
    datetime_utc TIMESTAMPTZ(0) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS btc_eth_gap_avg_5m_indicator (
    id SERIAL PRIMARY KEY,
    btc_eth_gap_avg_5m NUMERIC(15,4),
    datetime_utc TIMESTAMPTZ(0) NOT NULL UNIQUE,
    btc_usd_id INT NOT NULL REFERENCES btc_usd(id),
    eth_usd_id INT NOT NULL REFERENCES eth_usd(id)
);