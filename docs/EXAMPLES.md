# Usage Examples

Practical examples of using the ClickHouse OHLCV API.

---

## Table of Contents

1. [Python Examples](#python-examples)
2. [JavaScript Examples](#javascript-examples)
3. [cURL Examples](#curl-examples)
4. [Advanced Use Cases](#advanced-use-cases)

---

## Python Examples

### Basic Usage

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Get OHLCV data
response = requests.get(
    f"{BASE_URL}/api/v1/ohlcv",
    params={
        "symbol": "BINANCE:BTCUSDT.P",
        "start": "20250701-0000",
        "end": "20250801-0000",
        "limit": 1000
    }
)

data = response.json()
print(f"Retrieved {data['metadata']['total_records']} records")

for candle in data['data']:
    print(f"{candle['candle_time']}: {candle['close']}")
```

### With Error Handling

```python
import requests
from typing import Dict, List, Optional

class OHLCVClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def get_ohlcv(
        self,
        symbol: str,
        start: str,
        end: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> Dict:
        """Get OHLCV data with error handling."""
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
                raise ValueError(f"Validation error: {error_data['message']}")
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

try:
    data = client.get_ohlcv(
        symbol="BINANCE:BTCUSDT.P",
        start="20250701-0000",
        end="20250801-0000"
    )
    print(f"Success! Got {len(data['data'])} records")
    
except ValueError as e:
    print(f"Invalid input: {e}")
except ConnectionError as e:
    print(f"Connection error: {e}")
```

### Pagination Example

```python
def fetch_all_data(symbol: str, start: str, end: str) -> List[Dict]:
    """Fetch all data using pagination."""
    all_data = []
    offset = 0
    limit = 1000
    
    while True:
        response = requests.get(
            f"{BASE_URL}/api/v1/ohlcv",
            params={
                "symbol": symbol,
                "start": start,
                "end": end,
                "limit": limit,
                "offset": offset
            }
        )
        
        data = response.json()
        all_data.extend(data['data'])
        
        # Check if more data available
        if not data['metadata']['has_more']:
            break
        
        offset += limit
        print(f"Fetched {len(all_data)} records so far...")
    
    return all_data

# Usage
all_candles = fetch_all_data(
    symbol="BINANCE:BTCUSDT.P",
    start="20250101-0000",
    end="20251231-2359"
)
print(f"Total records: {len(all_candles)}")
```

### Async Python Example

```python
import aiohttp
import asyncio
from typing import List

async def fetch_ohlcv_async(
    session: aiohttp.ClientSession,
    symbol: str,
    start: str,
    end: str
) -> Dict:
    """Async fetch OHLCV data."""
    url = f"{BASE_URL}/api/v1/ohlcv"
    params = {
        "symbol": symbol,
        "start": start,
        "end": end
    }
    
    async with session.get(url, params=params) as response:
        return await response.json()

async def fetch_multiple_symbols(symbols: List[str], start: str, end: str):
    """Fetch data for multiple symbols concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_ohlcv_async(session, symbol, start, end)
            for symbol in symbols
        ]
        results = await asyncio.gather(*tasks)
        return results

# Usage
symbols = [
    "BINANCE:BTCUSDT.P",
    "BINANCE:ETHUSDT.P",
    "BINANCE:BNBUSDT.P"
]

results = asyncio.run(
    fetch_multiple_symbols(
        symbols,
        start="20250701-0000",
        end="20250801-0000"
    )
)

for i, data in enumerate(results):
    print(f"{symbols[i]}: {len(data['data'])} records")
```

---

## JavaScript Examples

### Node.js with Axios

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Get OHLCV data
async function getOHLCV(symbol, start, end, limit = 1000) {
    try {
        const response = await axios.get(`${BASE_URL}/api/v1/ohlcv`, {
            params: {
                symbol,
                start,
                end,
                limit
            }
        });
        
        return response.data;
    } catch (error) {
        if (error.response) {
            console.error('API Error:', error.response.data);
        } else {
            console.error('Request Error:', error.message);
        }
        throw error;
    }
}

// Usage
(async () => {
    const data = await getOHLCV(
        'BINANCE:BTCUSDT.P',
        '20250701-0000',
        '20250801-0000'
    );
    
    console.log(`Retrieved ${data.metadata.total_records} records`);
    data.data.forEach(candle => {
        console.log(`${candle.candle_time}: ${candle.close}`);
    });
})();
```

### Browser Fetch API

```javascript
// Get OHLCV data
async function fetchOHLCV(symbol, start, end) {
    const url = new URL('http://localhost:8000/api/v1/ohlcv');
    url.searchParams.append('symbol', symbol);
    url.searchParams.append('start', start);
    url.searchParams.append('end', end);
    
    const response = await fetch(url);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
    }
    
    return await response.json();
}

// Usage
fetchOHLCV('BINANCE:BTCUSDT.P', '20250701-0000', '20250801-0000')
    .then(data => {
        console.log('Data:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
```

### React Hook Example

```javascript
import { useState, useEffect } from 'react';

function useOHLCV(symbol, start, end) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            
            try {
                const url = new URL('http://localhost:8000/api/v1/ohlcv');
                url.searchParams.append('symbol', symbol);
                url.searchParams.append('start', start);
                if (end) url.searchParams.append('end', end);
                
                const response = await fetch(url);
                
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                
                const result = await response.json();
                setData(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        
        fetchData();
    }, [symbol, start, end]);
    
    return { data, loading, error };
}

// Usage in component
function OHLCVChart({ symbol }) {
    const { data, loading, error } = useOHLCV(
        symbol,
        '20250701-0000',
        '20250801-0000'
    );
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    
    return (
        <div>
            <h2>{symbol}</h2>
            <p>Records: {data.metadata.total_records}</p>
            {/* Render chart here */}
        </div>
    );
}
```

---

## cURL Examples

### Basic Request

```bash
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=20250701-0000&end=20250801-0000"
```

### With Pretty Print (jq)

```bash
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=20250701-0000&end=20250801-0000" | jq '.'
```

### Get Latest Candle

```bash
curl "http://localhost:8000/api/v1/ohlcv/latest?symbol=BINANCE:BTCUSDT.P"
```

### With Pagination

```bash
# First page
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=20250701-0000&limit=100&offset=0"

# Second page
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=20250701-0000&limit=100&offset=100"
```

### Save Response to File

```bash
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=20250701-0000" \
  -o btc_data.json
```

### With Request Headers

```bash
curl "http://localhost:8000/api/v1/ohlcv?symbol=BINANCE:BTCUSDT.P&start=20250701-0000" \
  -H "User-Agent: MyApp/1.0" \
  -v
```

---

## Advanced Use Cases

### 1. Data Export to CSV

```python
import requests
import csv
from datetime import datetime

def export_to_csv(symbol: str, start: str, end: str, filename: str):
    """Export OHLCV data to CSV file."""
    response = requests.get(
        f"{BASE_URL}/api/v1/ohlcv",
        params={
            "symbol": symbol,
            "start": start,
            "end": end,
            "limit": 10000
        }
    )
    
    data = response.json()
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['candle_time', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for candle in data['data']:
            writer.writerow(candle)
    
    print(f"Exported {len(data['data'])} records to {filename}")

# Usage
export_to_csv(
    symbol="BINANCE:BTCUSDT.P",
    start="20250701-0000",
    end="20250801-0000",
    filename="btc_july_2025.csv"
)
```

### 2. Data Analysis with Pandas

```python
import requests
import pandas as pd

def get_ohlcv_dataframe(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Get OHLCV data as pandas DataFrame."""
    response = requests.get(
        f"{BASE_URL}/api/v1/ohlcv",
        params={
            "symbol": symbol,
            "start": start,
            "end": end,
            "limit": 10000
        }
    )
    
    data = response.json()
    df = pd.DataFrame(data['data'])
    df['candle_time'] = pd.to_datetime(df['candle_time'])
    df = df.set_index('candle_time')
    
    return df

# Usage
df = get_ohlcv_dataframe(
    symbol="BINANCE:BTCUSDT.P",
    start="20250701-0000",
    end="20250801-0000"
)

# Calculate statistics
print("Summary Statistics:")
print(df[['open', 'high', 'low', 'close', 'volume']].describe())

# Calculate returns
df['returns'] = df['close'].pct_change()
print(f"\nAverage return: {df['returns'].mean():.4f}")
print(f"Volatility: {df['returns'].std():.4f}")
```

### 3. Real-time Monitoring

```python
import requests
import time
from datetime import datetime, timedelta

def monitor_symbol(symbol: str, interval_seconds: int = 60):
    """Monitor latest price for a symbol."""
    while True:
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/ohlcv/latest",
                params={"symbol": symbol}
            )
            
            if response.ok:
                data = response.json()
                print(f"[{datetime.now()}] {symbol}: ${data['close']:,.2f}")
            else:
                print(f"Error: {response.status_code}")
            
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(interval_seconds)

# Usage - Monitor BTC price every minute
monitor_symbol("BINANCE:BTCUSDT.P", interval_seconds=60)
```

### 4. Batch Processing Multiple Symbols

```python
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_symbol_data(symbol: str, start: str, end: str) -> Dict:
    """Fetch data for a single symbol."""
    response = requests.get(
        f"{BASE_URL}/api/v1/ohlcv",
        params={
            "symbol": symbol,
            "start": start,
            "end": end
        }
    )
    return {
        "symbol": symbol,
        "data": response.json(),
        "status": "success" if response.ok else "failed"
    }

def fetch_multiple_symbols(symbols: List[str], start: str, end: str, max_workers: int = 5):
    """Fetch data for multiple symbols in parallel."""
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_symbol = {
            executor.submit(fetch_symbol_data, symbol, start, end): symbol
            for symbol in symbols
        }
        
        # Process completed tasks
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                result = future.result()
                results[symbol] = result
                print(f"✓ {symbol}: {result['status']}")
            except Exception as e:
                print(f"✗ {symbol}: {str(e)}")
                results[symbol] = {"status": "error", "error": str(e)}
    
    return results

# Usage
symbols = [
    "BINANCE:BTCUSDT.P",
    "BINANCE:ETHUSDT.P",
    "BINANCE:BNBUSDT.P",
    "BINANCE:ADAUSDT.P",
    "BINANCE:SOLUSDT.P"
]

results = fetch_multiple_symbols(
    symbols,
    start="20250701-0000",
    end="20250801-0000",
    max_workers=5
)

# Summary
successful = sum(1 for r in results.values() if r['status'] == 'success')
print(f"\nFetched {successful}/{len(symbols)} symbols successfully")
```

### 5. Caching with Redis

```python
import requests
import redis
import json
from typing import Optional

class CachedOHLCVClient:
    def __init__(self, base_url: str, redis_url: str = "redis://localhost:6379"):
        self.base_url = base_url
        self.redis_client = redis.from_url(redis_url)
        self.cache_ttl = 300  # 5 minutes
    
    def _get_cache_key(self, symbol: str, start: str, end: str) -> str:
        """Generate cache key."""
        return f"ohlcv:{symbol}:{start}:{end}"
    
    def get_ohlcv(self, symbol: str, start: str, end: str) -> Dict:
        """Get OHLCV data with caching."""
        # Check cache first
        cache_key = self._get_cache_key(symbol, start, end)
        cached = self.redis_client.get(cache_key)
        
        if cached:
            print("Cache hit!")
            return json.loads(cached)
        
        # Fetch from API
        print("Cache miss, fetching from API...")
        response = requests.get(
            f"{self.base_url}/api/v1/ohlcv",
            params={"symbol": symbol, "start": start, "end": end}
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Store in cache
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(data)
        )
        
        return data

# Usage
client = CachedOHLCVClient(BASE_URL)

# First call - cache miss
data1 = client.get_ohlcv("BINANCE:BTCUSDT.P", "20250701-0000", "20250801-0000")

# Second call - cache hit
data2 = client.get_ohlcv("BINANCE:BTCUSDT.P", "20250701-0000", "20250801-0000")
```

---

## Error Handling Best Practices

```python
import requests
from typing import Optional

def safe_api_call(
    endpoint: str,
    params: dict,
    max_retries: int = 3,
    retry_delay: int = 1
) -> Optional[Dict]:
    """Make API call with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                params=params,
                timeout=30
            )
            
            if response.ok:
                return response.json()
            
            # Handle specific status codes
            if response.status_code == 422:
                # Validation error - don't retry
                error = response.json()
                raise ValueError(f"Validation error: {error['message']}")
            
            if response.status_code == 503:
                # Service unavailable - retry
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise ConnectionError("Service unavailable after retries")
            
            # Other errors
            response.raise_for_status()
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise TimeoutError("Request timed out after retries")
        
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise ConnectionError("Connection failed after retries")
    
    return None

# Usage
try:
    data = safe_api_call(
        "/api/v1/ohlcv",
        params={
            "symbol": "BINANCE:BTCUSDT.P",
            "start": "20250701-0000"
        }
    )
    print("Success!")
except ValueError as e:
    print(f"Invalid input: {e}")
except (ConnectionError, TimeoutError) as e:
    print(f"Request failed: {e}")
```

---

## Need More Help?

- **API Documentation**: See [API.md](API.md)
- **Interactive Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues
