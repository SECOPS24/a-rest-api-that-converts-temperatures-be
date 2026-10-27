from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(
    title="Temperature Converter API",
    description="A REST API that converts temperatures between Celsius and Fahrenheit",
    version="1.0.0"
)


class ConversionResult(BaseModel):
    input_value: float
    input_unit: str
    output_value: float
    output_unit: str
    formula: str


class BulkConversionRequest(BaseModel):
    values: list[float]
    from_unit: str
    to_unit: str


class BulkConversionResult(BaseModel):
    from_unit: str
    to_unit: str
    conversions: list[dict]


def celsius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9


def round_to_4(value: float) -> float:
    return round(value, 4)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.get("/", tags=["Info"])
def root():
    return {
        "name": "Temperature Converter API",
        "version": "1.0.0",
        "description": "Convert temperatures between Celsius and Fahrenheit",
        "endpoints": {
            "health": "GET /health",
            "celsius_to_fahrenheit": "GET /convert/celsius-to-fahrenheit?value={value}",
            "fahrenheit_to_celsius": "GET /convert/fahrenheit-to-celsius?value={value}",
            "generic_convert": "GET /convert?value={value}&from={unit}&to={unit}",
            "bulk_convert": "POST /convert/bulk",
            "docs": "GET /docs"
        }
    }


@app.get("/convert/celsius-to-fahrenheit", response_model=ConversionResult, tags=["Conversion"])
def convert_celsius_to_fahrenheit(
    value: float = Query(..., description="Temperature value in Celsius")
):
    """
    Convert a temperature from Celsius to Fahrenheit.

    Formula: (°C × 9/5) + 32 = °F
    """
    result = celsius_to_fahrenheit(value)
    return ConversionResult(
        input_value=value,
        input_unit="Celsius",
        output_value=round_to_4(result),
        output_unit="Fahrenheit",
        formula=f"({value} × 9/5) + 32 = {round_to_4(result)}"
    )


@app.get("/convert/fahrenheit-to-celsius", response_model=ConversionResult, tags=["Conversion"])
def convert_fahrenheit_to_celsius(
    value: float = Query(..., description="Temperature value in Fahrenheit")
):
    """
    Convert a temperature from Fahrenheit to Celsius.

    Formula: (°F - 32) × 5/9 = °C
    """
    result = fahrenheit_to_celsius(value)
    return ConversionResult(
        input_value=value,
        input_unit="Fahrenheit",
        output_value=round_to_4(result),
        output_unit="Celsius",
        formula=f"({value} - 32) × 5/9 = {round_to_4(result)}"
    )


@app.get("/convert", response_model=ConversionResult, tags=["Conversion"])
def generic_convert(
    value: float = Query(..., description="Temperature value to convert"),
    from_unit: str = Query(..., alias="from", description="Source unit: 'celsius' or 'fahrenheit'"),
    to_unit: str = Query(..., alias="to", description="Target unit: 'celsius' or 'fahrenheit'")
):
    """
    Generic temperature conversion endpoint.

    Specify source and target units using the `from` and `to` query parameters.
    Accepted values: `celsius` (or `c`), `fahrenheit` (or `f`).
    """
    from_normalized = from_unit.strip().lower()
    to_normalized = to_unit.strip().lower()

    celsius_aliases = {"celsius", "c"}
    fahrenheit_aliases = {"fahrenheit", "f"}
    valid_units = celsius_aliases | fahrenheit_aliases

    if from_normalized not in valid_units:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid 'from' unit: '{from_unit}'. Use 'celsius' or 'fahrenheit'."
        )

    if to_normalized not in valid_units:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid 'to' unit: '{to_unit}'. Use 'celsius' or 'fahrenheit'."
        )

    from_is_celsius = from_normalized in celsius_aliases
    to_is_celsius = to_normalized in celsius_aliases

    if from_is_celsius == to_is_celsius:
        unit_label = "Celsius" if from_is_celsius else "Fahrenheit"
        return ConversionResult(
            input_value=value,
            input_unit=unit_label,
            output_value=round_to_4(value),
            output_unit=unit_label,
            formula=f"No conversion needed: {value} {unit_label} = {value} {unit_label}"
        )

    if from_is_celsius:
        result = celsius_to_fahrenheit(value)
        return ConversionResult(
            input_value=value,
            input_unit="Celsius",
            output_value=round_to_4(result),
            output_unit="Fahrenheit",
            formula=f"({value} × 9/5) + 32 = {round_to_4(result)}"
        )
    else:
        result = fahrenheit_to_celsius(value)
        return ConversionResult(
            input_value=value,
            input_unit="Fahrenheit",
            output_value=round_to_4(result),
            output_unit="Celsius",
            formula=f"({value} - 32) × 5/9 = {round_to_4(result)}"
        )


@app.post("/convert/bulk", response_model=BulkConversionResult, tags=["Conversion"])
def bulk_convert(request: BulkConversionRequest):
    """
    Convert multiple temperature values in a single request.

    Provide a list of values and specify the source and target units.
    Accepted units: `celsius` (or `c`), `fahrenheit` (or `f`).
    """
    celsius_aliases = {"celsius", "c"}
    fahrenheit_aliases = {"fahrenheit", "f"}
    valid_units = celsius_aliases | fahrenheit_aliases

    from_normalized = request.from_unit.strip().lower()
    to_normalized = request.to_unit.strip().lower()

    if from_normalized not in valid_units:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid 'from_unit': '{request.from_unit}'. Use 'celsius' or 'fahrenheit'."
        )

    if to_normalized not in valid_units:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid 'to_unit': '{request.to_unit}'. Use 'celsius' or 'fahrenheit'."
        )

    if not request.values:
        raise HTTPException(status_code=400, detail="'values' list must not be empty.")

    if len(request.values) > 1000:
        raise HTTPException(status_code=400, detail="Maximum of 1000 values allowed per request.")

    from_is_celsius = from_normalized in celsius_aliases
    to_is_celsius = to_normalized in celsius_aliases

    from_label = "Celsius" if from_is_celsius else "Fahrenheit"
    to_label = "Celsius" if to_is_celsius else "Fahrenheit"

    conversions = []
    for val in request.values:
        if from_is_celsius == to_is_celsius:
            converted = val
        elif from_is_celsius:
            converted = celsius_to_fahrenheit(val)
        else:
            converted = fahrenheit_to_celsius(val)

        conversions.append({
            "input": val,
            "output": round_to_4(converted)
        })

    return BulkConversionResult(
        from_unit=from_label,
        to_unit=to_label,
        conversions=conversions
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
