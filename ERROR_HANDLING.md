# Checkout API Error Handling Strategy

## Validation

`CheckoutRequest` validates both identifiers as UUIDs. FastAPI/Pydantic rejects malformed JSON input with HTTP `422 Unprocessable Entity` before the checkout handler runs.

Business validation uses custom exceptions and returns HTTP `400` for invalid checkout state, such as an empty cart or non-positive cart quantity.

## Resource errors

- `404 User not found`
- `404 Shipping address not found for this user`
- `404 No active cart found for this user`
- `404 Product not found`

## Conflict errors

- `409 Product unavailable`
- `409 Insufficient stock`

`409 Conflict` is used when the request is structurally valid but cannot be completed because the current resource state prevents checkout.

## Database errors

SQLAlchemy errors are rolled back and converted to a generic HTTP `500` response. Internal SQL/database details are intentionally not returned to clients.

## Transaction safety

The checkout validates all cart items before creating the order. If an expected checkout error or database error occurs, the SQLAlchemy session is rolled back so a partial order is not committed.

## Tests

`tests/test_checkout.py` covers:

- successful checkout (`201`)
- empty cart (`400`)
- missing product (`404`)
- insufficient stock (`409`)
- malformed UUID input (`422`)
- missing user (`404`)
