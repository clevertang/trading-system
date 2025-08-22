# Risk Package

This package provides risk management and position sizing functionality.

## Components

### `position_sizing.py`
Position sizing calculations and risk controls.

**Key Functions:**
- `calculate_position_size(available_cash, target_allocation, current_price, max_position_pct)` - Determine appropriate share quantity
- `check_margin_requirements(orders, available_cash, margin_multiplier)` - Validate buying power

## Usage

```python
from trading.risk.position_sizing import calculate_position_size, check_margin_requirements

# Calculate position size with 10% maximum allocation
shares = calculate_position_size(
    available_cash=100000,
    target_allocation=5000,
    current_price=150.00,
    max_position_pct=0.10
)

# Check if orders are within margin requirements
can_execute = check_margin_requirements(
    orders=pending_orders,
    available_cash=50000,
    margin_multiplier=2.0  # 2:1 margin account
)
```

## Risk Controls

### Position Sizing
- **Maximum Position Percentage**: Limits single position as % of available cash
- **Allocation Constraints**: Respects target allocation vs maximum allowed
- **Share Calculation**: Rounds down to avoid exceeding allocation

### Margin Management
- **Buying Power**: Supports cash (1:1) and margin (2:1) accounts
- **Order Validation**: Checks total cash requirement vs available funds
- **Risk Prevention**: Prevents over-leveraging

## Default Parameters

- `max_position_pct`: 10% (prevents concentration risk)
- `margin_multiplier`: 1.0 (cash account, no leverage)

## Integration

Risk controls should be applied before order execution:
1. Calculate position sizes with risk constraints
2. Validate margin requirements
3. Generate orders within risk limits
4. Execute through execution engine