# Data

This project uses a **synthetic dataset** generated from realistic B2B procurement parameters.

## Files

| File | Rows | Description |
|------|------|-------------|
| `customer_orders.csv` | 20,000 | Customer order details, basket size, delivery status |
| `supplier_orders.csv` | ~15,000 | Supplier purchase orders, lead times, on-time status |
| `customers.csv` | 500 | Customer profiles: city, technician level, work situation |
| `products.csv` | 300 | SKU master: category, pricing, criticality |
| `suppliers.csv` | 30 | Supplier master: country, reliability score, lead time |

## How to generate the data

The CSV files are not included in this repository. To generate them, run the simulation script from the root folder:

```bash
python data_simulation.py
```

This will create all required CSV files in the working directory. Move them to this `data/` folder before running the notebook.

## How the data was generated

See `data_simulation.py` in the root folder for the full simulation code with documented parameters.

Key parameters modelling real B2B patterns:
- Basket size scales with technician level (Maintenance Engineers order more)
- Remote cities (Dresden, Nuremberg) have higher delivery delays
- Asian suppliers have lower reliability scores than German/Dutch ones
- Return rates are higher for Junior Technicians (wrong part selection)
