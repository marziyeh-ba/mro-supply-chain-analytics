# B2B MRO Supply Chain Analytics
### End-to-End Procurement & Customer Engagement Analysis

**Tools:** Python · Pandas · DuckDB · scikit-learn  
**Domain:** B2B industrial tools & MRO distribution — Germany  
**Status:** Portfolio project | Based on real B2B procurement experience

---

## Business Problems

Two problems that every B2B distributor without a large central warehouse faces:

1. **Basket size** — getting customers to order complete kits rather than single items
2. **End-to-end order management** — tracking and improving the full cycle from customer order → supplier order → delivery, with no warehouse buffer

## What the Analysis Covers

| Section | Business Question |
|---------|------------------|
| Customer Engagement | Which segments buy the most? What drives basket growth? |
| Delivery Performance | How consistent is on-time performance across cities? What is driving network-wide delays? |
| SQL Queries (DuckDB) | Basket growth YoY, high-risk suppliers, churn risk, segment matrix |
| RFM Segmentation | Which customers are Champions, At Risk, or Lost? |
| K-Means Clustering (k=4) | What natural customer groups exist in the data? |

## Key Findings

- **Maintenance Engineers** order 2.4× more items per order than Junior Technicians
- **Junior Technicians** have a return rate ~2× higher — wrong parts, fragmented orders
- **At Risk segment** revenue is significant — reachable with targeted outreach  
- **K=4** clustering reveals four distinct behaviours vs the oversimplified k=2 baseline
- **Delivery on-time rate below 60% across all cities** — gap between best and worst is only 3.3 points, pointing to a network-wide reliability issue rather than isolated route problems
- **High-risk suppliers** (high value, low reliability) identified for dual-sourcing strategy

## Project Structure

```
mro-supply-chain-analytics/
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/
│   └── mro_supply_chain_analysis.ipynb
├── reports/
│   └── figures/
│       ├── chart1_kpi_dashboard.png
│       ├── chart2_customer_engagement.png
│       ├── chart3_delivery_performance.png
│       ├── chart4_supplier_performance.png
│       ├── chart5_product_analysis.png
│       ├── chart6_rfm_analysis.png
│       └── chart7_clustering.png
├── src/
│   └── utils.py
└── data/
    └── README.md
```

## Dataset

Synthetic dataset modelling a real B2B MRO distributor:
- 20,000 customer orders (2022–2023)
- 500 customers across 8 German cities
- 300 SKUs across 6 product categories
- 30 suppliers across 7 countries

Data parameters derived from real B2B procurement experience and validated against industry benchmarks.

## How to Run

```bash
pip install -r requirements.txt
jupyter notebook notebooks/mro_supply_chain_analysis.ipynb
```

---
*Marziyeh Eslamparasti | Business Analyst | Hamburg, Germany*  
[LinkedIn](https://linkedin.com/in/marziyeh-eslamparasti) · [GitHub](https://github.com/marziyeh-ba)
