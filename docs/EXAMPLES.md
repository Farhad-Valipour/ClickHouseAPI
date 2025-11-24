# Usage Examples

Practical examples of using the ClickHouse OHLCV API with ISO 8601 time format.

---

## Table of Contents

1. [Python Examples](#python-examples)
2. [JavaScript Examples](#javascript-examples)
3. [cURL Examples](#curl-examples)
4. [Advanced Use Cases](#advanced-use-cases)
5. [Migration from Legacy Format](#migration-from-legacy-format)

---

## Python Examples

### Basic Usage (ISO 8601)

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Get OHLCV data with ISO 8601 format (recommended)
response = requests.get(
    f"{BASE_URL}/api/v1/ohlcv",
    params={
        "symbol": "BINANCE:BTCUSDT.P",
        "start": "2025-07-01T00:00:00Z",
        "end": "2025-08-01T00:00:00Z",
        "limit": 1000
    }
)

data = response.json()
print(f"Retrieved {data['metadata']['total_records']} records")

for candle in data['data']:
    print(f"{candle['candle_time']}: {candle['close']}")
```

### With Timezone Support

```python
import requests

# Get data with specific timezone offset
response = requests.get(
    f"{BASE_URL}/api/v1/ohlcv",
    params={
        "symbol": "BINANCE:BTCUSDT.P",
        "start": "2025-07-01T00:00:00+03:00",  # UTC+3
        "end": "2025-08-01T00:00:00+03:00",
        "limit": 1000
    }
)

data = response.json()
```

### With Error Handling

```python
import requests
from typing import Dict, List, Optional
from datetime import datetime, timezone

class OHLCVClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def get_ohlcv(
        self,
        symbol: str,
        start: str,  # ISO 8601 format
        end: Optional[str] = None,  # ISO 8601 format
        limit: int = 1000,
        offset: int = 0
    ) -> Dict:
        """
        Get OHLCV data with error handling.
        
        Args:
            symbol: Trading symbol (e.g., 'BINANCE:BTCUSDT.P')
            start: Start time in ISO 8601 format (e.g., '2025-07-01T00:00:00Z')
            end: End time in ISO 8601 format (optional)
            limit: Maximum number of records
            offset: Number of records to skip
            
        Returns:
            API response as dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/ohlcv",
                params={
                    "symbol": symbol,
                    "start": start,
                    "end": end,
                    "limit": limit,
                    "offset": offset
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                error_data = e.response.json()
                raise ValueError(f"Validation error: {error_data['detail']}")
            elif e.response.status_code == 503:
                raise ConnectionError("Database unavailable")
            else:
                raise
        
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out")
        
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Request failed: {str(e)}")
    
    def get_latest(self, symbol: str) -> Dict:
        """Get latest candle for a symbol."""
        response = requests.get(
            f"{self.base_url}/api/v1/ohlcv/latest",
            params={"symbol": symbol}
        )
        response.raise_for_status()
        return response.json()

# Usage
client = OHLCVClient()
data = client.get_ohlcv(
    symbol="BINANCE:BTCUSDT.P",
    start="2025-07-01T00:00:00Z",
    end="2025-08-01T00:00:00Z"
)
```

### With Datetime Conversion

```python
import requests
from datetime import datetime, timezone

def get_ohlcv_by_datetime(
    symbol: str,
    start_dt: datetime,
    end_dt: datetime,
    limit: int = 1000
):
    """
    Get OHLCV data using Python datetime objects.
    Automatically converts to ISO 8601 format.
    """
    # Convert datetime to ISO 8601 string
    start_str = start_dt.isoformat()
    end_str = end_dt.isoformat()
    
    response = requests.get(
        "http://localhost:8000/api/v1/ohlcv",
        params={
            "symbol": symbol,
            "start": start_str,
            "end": end_str,
            "limit": limit
        }
    )
    
    return response.json()

# Usage with datetime objects
from datetime import datetime, timezone

start = datetime(2025, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
end = datetime(2025, 8, 1, 0, 0, 0, tzinfo=timezone.utc)

data = get_ohlcv_by_datetime(
    symbol="BINANCE:BTCUSDT.P",
    start_dt=start,
    end_dt=end
)
```

### Pagination Example

```python
import requests

def get_all_data(symbol: str, start: str, end: str):
    """Fetch all data using pagination."""
    all_data = []
    offset = 0
    limit = 1000
    
    while True:
        response = requests.get(
            "http://localhost:8000/api/v1/ohlcv",
            params={
                "symbol": symbol,
                "start": start,
                "end": end,
                "limit": limit,
                "offset": offset
            }
        )
        
        result = response.json()
        all_data.extend(result['data'])
        
        # Check if there's more data
        if not result['metadata']['has_more']:
            break
            
        offset += limit
    
    return all_data

# Get all data for a year
all_candles = get_all_data(
    symbol="BINANCE:BTCUSDT.P",
    start="2025-01-01T00:00:00Z",
    end="2025-12-31T23:59:59Z"
)
print(f"Total candles: {len(all_candles)}")
```

### With Pandas Integration

```python
import requests
import pandas as pd
from datetime import datetime, timezone

def get_ohlcv_dataframe(
    symbol: str,
    start: str,
    end: str,
    limit: int = 10000
) -> pd.DataFrame:
    """
    Get OHLCV data as a pandas DataFrame.
    
    Args:
        symbol: Trading symbol
        start: Start time in ISO 8601 format
        end: End time in ISO 8601 format
        limit: Maximum records
        
    Returns:
        pandas DataFrame with OHLCV data
    """
    response = requests.get(
        "http://localhost:8000/api/v1/ohlcv",
        params={
            "symbol": symbol,
            "start": start,
            "end": end,
            "limit": limit
        }
    )
    
    data = response.json()
    df = pd.DataFrame(data['data'])
    
    # Convert candle_time to datetime
    df['candle_time'] = pd.to_datetime(df['candle_time'])
    
    # Set as index
    df.set_index('candle_time', inplace=True)
    
    return df

# Usage
df = get_ohlcv_dataframe(
    symbol="BINANCE:BTCUSDT.P",
    start="2025-07-01T00:00:00Z",
    end="2025-08-01T00:00:00Z"
)

# Analyze
print(df.describe())
print(f"Average close: ${df['close'].mean():.2f}")
print(f"Max price: ${df['high'].max():.2f}")
print(f"Min price: ${df['low'].min():.2f}")
```

### Async Example with aiohttp

```python
import asyncio
import aiohttp
from typing import List, Dict

async def fetch_ohlcv(
    session: aiohttp.ClientSession,
    symbol: str,
    start: str,
    end: str
) -> Dict:
    """Fetch OHLCV data asynchronously."""
    async with session.get(
        "http://localhost:8000/api/v1/ohlcv",
        params={
            "symbol": symbol,
            "start": start,
            "end": end,
            "limit": 1000
        }
    ) as response:
        return await response.json()

async def fetch_multiple_symbols(symbols: List[str]):
    """Fetch data for multiple symbols concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_ohlcv(
                session,
                symbol,
                "2025-07-01T00:00:00Z",
                "2025-08-01T00:00:00Z"
            )
            for symbol in symbols
        ]
        
        results = await asyncio.gather(*tasks)
        return results

# Usage
symbols = [
    "BINANCE:BTCUSDT.P",
    "BINANCE:ETHUSDT.P",
    "BINANCE:SOLUSDT.P"
]

results = asyncio.run(fetch_multiple_symbols(symbols))
for result in results:
    print(f"Got {result['metadata']['total_records']} records")
```

---

## JavaScript Examples

### Basic Usage (Node.js with fetch)

```javascript
// Using native fetch (Node.js 18+)
const BASE_URL = 'http://localhost:8000';

async function getOHLCV(symbol, start, end, limit = 1000) {
    const params = new URLSearchParams({
        symbol,
        start,
        end,
        limit: limit.toString()
    });
    
    const response = await fetch(`${BASE_URL}/api/v1/ohlcv?${params}`);
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
}

// Usage with ISO 8601
getOHLCV(
    'BINANCE:BTCUSDT.P',
    '2025-07-01T00:00:00Z',
    '2025-08-01T00:00:00Z'
).then(data => {
    console.log(`Retrieved ${data.metadata.total_records} records`);
    data.data.forEach(candle => {
        console.log(`${candle.candle_time}: ${candle.close}`);
    });
}).catch(error => {
    console.error('Error:', error);
});
```

### With Axios

```javascript
const axios = require('axios');

const client = axios.create({
    baseURL: 'http://localhost:8000',
    timeout: 30000,
});

async function getOHLCV(symbol, start, end, options = {}) {
    try {
        const response = await client.get('/api/v1/ohlcv', {
            params: {
                symbol,
                start,  // ISO 8601 format
                end,    // ISO 8601 format
                limit: options.limit || 1000,
                offset: options.offset || 0
            }
        });
        
        return response.data;
    } catch (error) {
        if (error.response) {
            // Request made but server responded with error
            if (error.response.status === 422) {
                throw new Error(`Validation error: ${error.response.data.detail}`);
            } else if (error.response.status === 503) {
                throw new Error('Database unavailable');
            }
        } else if (error.request) {
            // Request made but no response received
            throw new Error('No response from server');
        }
        throw error;
    }
}

// Usage
(async () => {
    try {
        const data = await getOHLCV(
            'BINANCE:BTCUSDT.P',
            '2025-07-01T00:00:00Z',
            '2025-08-01T00:00:00Z'
        );
        
        console.log(`Total records: ${data.metadata.total_records}`);
        console.log(`Query time: ${data.metadata.query_time_ms}ms`);
    } catch (error) {
        console.error('Error:', error.message);
    }
})();
```

### Browser Example

```javascript
// Modern browser with ES6+
class OHLCVClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }
    
    async getOHLCV(symbol, start, end, options = {}) {
        const params = new URLSearchParams({
            symbol,
            start,  // ISO 8601: '2025-07-01T00:00:00Z'
            end,    // ISO 8601: '2025-08-01T00:00:00Z'
            limit: options.limit || 1000,
            offset: options.offset || 0
        });
        
        const response = await fetch(`${this.baseURL}/api/v1/ohlcv?${params}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Request failed');
        }
        
        return await response.json();
    }
    
    async getLatest(symbol) {
        const params = new URLSearchParams({ symbol });
        const response = await fetch(`${this.baseURL}/api/v1/ohlcv/latest?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
}

// Usage
const client = new OHLCVClient();

// Get data
client.getOHLCV(
    'BINANCE:BTCUSDT.P',
    '2025-07-01T00:00:00Z',
    '2025-08-01T00:00:00Z'
).then(data => {
    console.log('Data:', data);
    
    // Update UI
    updateChart(data.data);
}).catch(error => {
    console.error('Error:', error);
    showError(error.message);
});
```

### With Date Objects

```javascript
// Convert JavaScript Date to ISO 8601
function dateToISO(date) {
    return date.toISOString();
}

// Usage
const start = new Date('2025-07-01T00:00:00Z');
const end = new Date('2025-08-01T00:00:00Z');

fetch('http://localhost:8000/api/v1/ohlcv?' + new URLSearchParams({
    symbol: 'BINANCE:BTCUSDT.P',
    start: dateToISO(start),
    end: dateToISO(end),
    limit: '1000'
}))
.then(response => response.json())
.then(data => console.log(data));
```

---

## cURL Examples

### Basic Request (ISO 8601)

```bash
# Get OHLCV data with ISO 8601 format (recommended)
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00Z&end=2025-08-01T00:00:00Z"
```

### With Pretty JSON Output

```bash
# Using jq for pretty printing
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00Z&end=2025-08-01T00:00:00Z" | jq '.'
```

### With Timezone Offset

```bash
# Using timezone offset
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00%2B03:00&end=2025-08-01T00:00:00%2B03:00"

# Note: URL encode + as %2B in the URL
```

### Pagination

```bash
# Get first page
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00Z&limit=100&offset=0"

# Get second page
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00Z&limit=100&offset=100"
```

### Save to File

```bash
# Save response to file
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00Z" \
    -o response.json

# Save with metadata
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=2025-07-01T00:00:00Z" \
    -w "\nHTTP Status: %{http_code}\nTime: %{time_total}s\n" \
    -o response.json
```

### Get Latest Candle

```bash
# Get latest candle for a symbol
curl "http://localhost:8000/api/v1/ohlcv/latest?symbol=BINANCE:BTCUSDT.P"
```

### Health Check

```bash
# Basic health check
curl "http://localhost:8000/health"

# Detailed health check
curl "http://localhost:8000/health/ready" | jq '.'
```

---

## Advanced Use Cases

### 1. Rate Calculation

```python
import requests
from typing import List, Dict

def calculate_returns(
    symbol: str,
    start: str,
    end: str
) -> List[Dict]:
    """Calculate price returns for each candle."""
    response = requests.get(
        "http://localhost:8000/api/v1/ohlcv",
        params={
            "symbol": symbol,
            "start": start,
            "end": end,
            "limit": 10000
        }
    )
    
    data = response.json()['data']
    
    for i in range(1, len(data)):
        prev_close = data[i-1]['close']
        curr_close = data[i]['close']
        data[i]['return'] = ((curr_close - prev_close) / prev_close) * 100
    
    return data

# Usage
returns = calculate_returns(
    symbol="BINANCE:BTCUSDT.P",
    start="2025-07-01T00:00:00Z",
    end="2025-08-01T00:00:00Z"
)

for candle in returns[1:]:  # Skip first (no return)
    print(f"{candle['candle_time']}: {candle['return']:.2f}%")
```

### 2. Moving Average

```python
import requests
from collections import deque

def calculate_sma(prices: List[float], period: int) -> List[float]:
    """Calculate Simple Moving Average."""
    sma = []
    queue = deque(maxlen=period)
    
    for price in prices:
        queue.append(price)
        if len(queue) == period:
            sma.append(sum(queue) / period)
        else:
            sma.append(None)
    
    return sma

# Get data
response = requests.get(
    "http://localhost:8000/api/v1/ohlcv",
    params={
        "symbol": "BINANCE:BTCUSDT.P",
        "start": "2025-07-01T00:00:00Z",
        "end": "2025-08-01T00:00:00Z",
        "limit": 10000
    }
)

data = response.json()['data']
closes = [candle['close'] for candle in data]

# Calculate 20-period SMA
sma_20 = calculate_sma(closes, 20)

# Print results
for i, candle in enumerate(data):
    if sma_20[i]:
        print(f"{candle['candle_time']}: Close={candle['close']:.2f}, SMA20={sma_20[i]:.2f}")
```

### 3. Volume Analysis

```python
import requests
import statistics

def analyze_volume(symbol: str, start: str, end: str):
    """Analyze trading volume statistics."""
    response = requests.get(
        "http://localhost:8000/api/v1/ohlcv",
        params={
            "symbol": symbol,
            "start": start,
            "end": end,
            "limit": 10000
        }
    )
    
    data = response.json()['data']
    volumes = [candle['volume'] for candle in data]
    
    return {
        'total_volume': sum(volumes),
        'avg_volume': statistics.mean(volumes),
        'median_volume': statistics.median(volumes),
        'max_volume': max(volumes),
        'min_volume': min(volumes),
        'std_dev': statistics.stdev(volumes) if len(volumes) > 1 else 0
    }

# Usage
stats = analyze_volume(
    symbol="BINANCE:BTCUSDT.P",
    start="2025-07-01T00:00:00Z",
    end="2025-08-01T00:00:00Z"
)

print("Volume Statistics:")
for key, value in stats.items():
    print(f"  {key}: {value:,.2f}")
```

### 4. Export to CSV

```python
import requests
import csv
from datetime import datetime

def export_to_csv(
    symbol: str,
    start: str,
    end: str,
    filename: str = "ohlcv_data.csv"
):
    """Export OHLCV data to CSV file."""
    response = requests.get(
        "http://localhost:8000/api/v1/ohlcv",
        params={
            "symbol": symbol,
            "start": start,
            "end": end,
            "limit": 10000
        }
    )
    
    data = response.json()['data']
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['candle_time', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for candle in data:
            writer.writerow(candle)
    
    print(f"Exported {len(data)} records to {filename}")

# Usage
export_to_csv(
    symbol="BINANCE:BTCUSDT.P",
    start="2025-07-01T00:00:00Z",
    end="2025-08-01T00:00:00Z",
    filename="btc_july_2025.csv"
)
```

### 5. Real-time Monitoring

```python
import requests
import time
from datetime import datetime, timezone

def monitor_price(symbol: str, interval_seconds: int = 60):
    """Monitor price in real-time."""
    print(f"Monitoring {symbol}...")
    
    while True:
        try:
            response = requests.get(
                "http://localhost:8000/api/v1/ohlcv/latest",
                params={"symbol": symbol}
            )
            
            if response.ok:
                data = response.json()
                candle = data['data'][0]
                
                now = datetime.now(timezone.utc).strftime("%H:%M:%S")
                print(f"[{now}] {symbol}: ${candle['close']:,.2f} | "
                      f"H: ${candle['high']:,.2f} | L: ${candle['low']:,.2f} | "
                      f"V: {candle['volume']:,.0f}")
            
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(interval_seconds)

# Usage
monitor_price("BINANCE:BTCUSDT.P", interval_seconds=30)
```

### 6. Multi-Symbol Comparison

```python
import requests
from typing import List, Dict

def compare_symbols(
    symbols: List[str],
    start: str,
    end: str
) -> Dict:
    """Compare performance across multiple symbols."""
    results = {}
    
    for symbol in symbols:
        response = requests.get(
            "http://localhost:8000/api/v1/ohlcv",
            params={
                "symbol": symbol,
                "start": start,
                "end": end,
                "limit": 10000
            }
        )
        
        data = response.json()['data']
        
        if data:
            first_close = data[0]['close']
            last_close = data[-1]['close']
            change_pct = ((last_close - first_close) / first_close) * 100
            
            results[symbol] = {
                'start_price': first_close,
                'end_price': last_close,
                'change_pct': change_pct,
                'candles': len(data)
            }
    
    return results

# Usage
comparison = compare_symbols(
    symbols=[
        "BINANCE:BTCUSDT.P",
        "BINANCE:ETHUSDT.P",
        "BINANCE:SOLUSDT.P"
    ],
    start="2025-07-01T00:00:00Z",
    end="2025-08-01T00:00:00Z"
)

print("Performance Comparison:")
for symbol, stats in comparison.items():
    print(f"\n{symbol}:")
    print(f"  Start: ${stats['start_price']:,.2f}")
    print(f"  End: ${stats['end_price']:,.2f}")
    print(f"  Change: {stats['change_pct']:+.2f}%")
    print(f"  Candles: {stats['candles']}")
```

---

## Migration from Legacy Format

### Quick Reference

**Legacy Format (Deprecated):**
```
YYYYMMDD-HHmm
Example: 20250701-0000
```

**ISO 8601 Format (Recommended):**
```
YYYY-MM-DDTHH:MM:SSZ
Example: 2025-07-01T00:00:00Z
```

### Python Migration Example

```python
# Before (Legacy)
response = requests.get(
    "http://localhost:8000/api/v1/ohlcv",
    params={
        "symbol": "BINANCE:BTCUSDT.P",
        "start": "20250701-0000",  # Legacy
        "end": "20250801-0000"      # Legacy
    }
)

# After (ISO 8601)
response = requests.get(
    "http://localhost:8000/api/v1/ohlcv",
    params={
        "symbol": "BINANCE:BTCUSDT.P",
        "start": "2025-07-01T00:00:00Z",  # ISO 8601
        "end": "2025-08-01T00:00:00Z"      # ISO 8601
    }
)
```

### Conversion Helper Function

```python
from datetime import datetime

def legacy_to_iso8601(legacy_time: str) -> str:
    """
    Convert legacy format to ISO 8601.
    
    Args:
        legacy_time: Time in format YYYYMMDD-HHmm
        
    Returns:
        Time in ISO 8601 format (UTC)
    """
    dt = datetime.strptime(legacy_time, "%Y%m%d-%H%M")
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

# Usage
legacy = "20250701-0000"
iso8601 = legacy_to_iso8601(legacy)
print(f"{legacy} → {iso8601}")
# Output: 20250701-0000 → 2025-07-01T00:00:00Z
```

### JavaScript Conversion

```javascript
function legacyToISO8601(legacyTime) {
    // Parse: YYYYMMDD-HHmm
    const year = legacyTime.substring(0, 4);
    const month = legacyTime.substring(4, 6);
    const day = legacyTime.substring(6, 8);
    const hour = legacyTime.substring(9, 11);
    const minute = legacyTime.substring(11, 13);
    
    return `${year}-${month}-${day}T${hour}:${minute}:00Z`;
}

// Usage
const legacy = "20250701-0000";
const iso8601 = legacyToISO8601(legacy);
console.log(`${legacy} → ${iso8601}`);
// Output: 20250701-0000 → 2025-07-01T00:00:00Z
```

---

## Best Practices

### 1. Always Use ISO 8601 for New Code

```python
# ✅ Good
start = "2025-07-01T00:00:00Z"

# ❌ Avoid (deprecated)
start = "20250701-0000"
```

### 2. Include Timezone Information

```python
# ✅ Explicit timezone (recommended)
start = "2025-07-01T00:00:00Z"           # UTC
start = "2025-07-01T00:00:00+03:00"      # UTC+3

# ⚠️ No timezone (assumes UTC)
start = "2025-07-01T00:00:00"
```

### 3. Use Native Date Objects

```python
# Python
from datetime import datetime, timezone
dt = datetime(2025, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
iso_string = dt.isoformat()  # "2025-07-01T00:00:00+00:00"
```

```javascript
// JavaScript
const date = new Date('2025-07-01T00:00:00Z');
const isoString = date.toISOString();  // "2025-07-01T00:00:00.000Z"
```

### 4. Handle Errors Gracefully

```python
try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 422:
        print("Invalid time format. Use ISO 8601.")
    else:
        print(f"Error: {e}")
```

### 5. Validate Time Formats

```python
from datetime import datetime

def validate_iso8601(time_str: str) -> bool:
    """Validate ISO 8601 format."""
    try:
        datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

# Usage
if validate_iso8601("2025-07-01T00:00:00Z"):
    # Make API call
    pass
```

---

## Additional Resources

- [ISO 8601 Standard](https://en.wikipedia.org/wiki/ISO_8601)
- [Python datetime documentation](https://docs.python.org/3/library/datetime.html)
- [JavaScript Date documentation](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date)
- [API Documentation](API.md)

---

## Support

For issues or questions:
- Check the [API Documentation](API.md)
- Review error messages for specific format requirements
- Ensure ISO 8601 format compliance
