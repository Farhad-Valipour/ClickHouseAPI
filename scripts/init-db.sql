-- ClickHouse Database Initialization Script
-- This script creates the OHLCV table with proper schema

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS default;

-- Use the database
USE default;

-- Create OHLCV table
CREATE TABLE IF NOT EXISTS ohlcv
(
    candle_time DateTime64(3),
    symbol String,
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Float64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(candle_time)
ORDER BY (symbol, candle_time)
SETTINGS index_granularity = 8192;

-- Create indexes for better query performance
-- Note: ClickHouse uses ORDER BY for primary key, so symbol and candle_time are already indexed

-- Insert sample data (optional - for testing)
-- Uncomment the following lines to insert sample data

/*
INSERT INTO ohlcv VALUES
    ('2025-07-01 00:00:00', 'BINANCE:BTCUSDT.P', 50000.0, 51000.0, 49500.0, 50500.0, 1234567.89),
    ('2025-07-01 00:01:00', 'BINANCE:BTCUSDT.P', 50500.0, 50800.0, 50300.0, 50600.0, 987654.32),
    ('2025-07-01 00:02:00', 'BINANCE:BTCUSDT.P', 50600.0, 50900.0, 50400.0, 50700.0, 876543.21),
    ('2025-07-01 00:00:00', 'BINANCE:ETHUSDT.P', 3000.0, 3050.0, 2980.0, 3020.0, 234567.89),
    ('2025-07-01 00:01:00', 'BINANCE:ETHUSDT.P', 3020.0, 3040.0, 3010.0, 3030.0, 198765.43);
*/
