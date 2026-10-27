# Temperature Converter API

A lightweight REST API built with FastAPI that converts temperatures between **Celsius** and **Fahrenheit**.

---

## Features

- Convert Celsius → Fahrenheit
- Convert Fahrenheit → Celsius
- Generic conversion endpoint with flexible unit aliases
- Bulk conversion (up to 1,000 values per request)
- Interactive Swagger UI docs
- Health check endpoint

---

## Getting Started

### Run with Docker

```bash
docker build -t temperature-converter .
docker run -p 3000:3000 temperature-converter
```

### Run locally

```bash
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:3000`.

---

## API Endpoints

### Health Check

```
GET /health
```

**Response:**
```json
{"status": "ok"}
```

---

### Celsius to Fahrenheit

```
GET /convert/celsius-to-fahrenheit?value={value}
```

**Example:**
```bash
curl "http://localhost:3000/convert/celsius-to-fahrenheit?value=100"
```

**Response:**
```json
{
  "input_value": 100.0,
  "input_unit": "Celsius",
  "output_value": 212.0,
  "output_unit": "Fahrenheit",
  "formula": "(100.0 × 9/5) + 32 = 212.0"
}
```

---

### Fahrenheit to Celsius

```
GET /convert/fahrenheit-to-celsius?value={value}
```

**Example:**
```bash
curl "http://localhost:3000/convert/fahrenheit-to-celsius?value=32"
```

**Response:**
```json
{
  "input_value": 32.0,
  "input_unit": "Fahrenheit",
  "output_value": 0.0,
  "output_unit": "Celsius",
  "formula": "(32.0 - 32) × 5/9 = 0.0"
}
```

---

### Generic Conversion

```
GET /convert?value={value}&from={unit}&to={unit}
```

Accepted unit values: `celsius`, `c`, `fahrenheit`, `f` (case-insensitive)

**Example:**
```bash
curl "http://localhost:3000/convert?value=37&from=celsius&to=fahrenheit"
```

**Response:**
```json
{
  "input_value": 37.0,
  "input_unit": "Celsius",
  "output_value": 98.6,
  "output_unit": "Fahrenheit",
  "formula": "(37.0 × 9/5) + 32 = 98.6"
}
```

---

### Bulk Conversion

```
POST /convert/bulk
Content-Type: application/json
```

**Request body:**
```json
{
  "values": [0, 100, -40, 37],
  "from_unit": "celsius",
  "to_unit": "fahrenheit"
}
```

**Response:**
```json
{
  "from_unit": "Celsius",
  "to_unit": "Fahrenheit",
  "conversions": [
    {"input": 0.0, "output": 32.0},
    {"input": 100.0, "output": 212.0},
    {"input": -40.0, "output": -40.0},
    {"input": 37.0, "output": 98.6}
  ]
}
```

---

## Interactive Docs

Once running, visit:

- **Swagger UI**: [http://localhost:3000/docs](http://localhost:3000/docs)
- **ReDoc**: [http://localhost:3000/redoc](http://localhost:3000/redoc)

---

## Conversion Formulas

| Conversion | Formula |
|---|---|
| Celsius → Fahrenheit | `(°C × 9/5) + 32` |
| Fahrenheit → Celsius | `(°F − 32) × 5/9` |

---

## Notes

- All output values are rounded to 4 decimal places.
- Bulk conversions support a maximum of **1,000 values** per request.
- Unit aliases are case-insensitive (`Celsius`, `celsius`, `C`, `c` are all valid).
