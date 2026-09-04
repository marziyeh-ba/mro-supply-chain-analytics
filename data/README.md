# Generated data

This project uses a reproducible synthetic dataset for a fictional B2B MRO distributor. No confidential company records are included.

## Generate the files

From the repository root, run:

```bash
python data_simulation.py
```

The script writes all five CSV files directly to this folder:

| File | Rows | Description |
|---|---:|---|
| `customer_orders.csv` | 20,000 | Basket, value, delivery, and return fields for customer orders |
| `supplier_orders.csv` | 15,000 | Procurement value, lead time, and supplier delivery fields |
| `customers.csv` | 500 | Customer city, technician level, work situation, and industry type |
| `products.csv` | 300 | SKU category, price, margin, criticality, and compatibility fields |
| `suppliers.csv` | 30 | Supplier country, assumed reliability score, and lead time |

Generated CSVs are excluded from Git. Re-run the script whenever a fresh local copy is needed.

## Scenario design

The script creates five related tables from a fixed random seed and transparent assumptions, including:

- eight customer cities;
- three technician levels;
- three work situations;
- ten product categories; and
- thirty suppliers across five countries.

These values are modelling inputs for a portfolio demonstration. They are not validated industry benchmarks or claims about real countries, suppliers, customers, or delivery networks. Analytical findings should be described as results of the simulated scenario.
