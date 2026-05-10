"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         B2B MRO SUPPLY CHAIN — SYNTHETIC DATASET SIMULATION                ║
║                                                                              ║
║  Author : Marziyeh Eslamparasti                                              ║
║  Purpose: Generate a realistic B2B MRO dataset for portfolio analysis        ║
║                                                                              ║
║  WHY SYNTHETIC DATA?                                                         ║
║  Real operational data from B2B businesses is confidential and cannot        ║
║  be shared publicly. Synthetic data — generated from real business           ║
║  logic and industry benchmarks — is the standard approach in data            ║
║  science portfolios and academic research. This exact approach was           ║
║  used in the author's Master's thesis (University of Europe, Hamburg).       ║
║                                                                              ║
║  HOW IT WORKS:                                                               ║
║  1. Define real business rules as parameters (city weights, skill            ║
║     levels, supplier reliability scores)                                     ║
║  2. Use those rules to CONSTRAIN the random generation — so the data         ║
║     follows real patterns, not pure randomness                               ║
║  3. Generate 5 interconnected tables that mirror a real database             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Fix random seed so results are reproducible
# (same seed = same data every time you run the script)
np.random.seed(42)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — BUSINESS PARAMETERS
# These are the "rules of the business" translated into numbers.
# Each parameter was chosen to reflect real industry patterns.
# ══════════════════════════════════════════════════════════════════════════════

# ── 1A: CITY PROFILES ─────────────────────────────────────────────────────────
# weight       = share of total customers in that city
#                (Hamburg = 20% because it is the largest industrial hub)
# delivery_days= how many days a standard order takes to arrive
#                (Hamburg = 1 day because it is close to main suppliers)
#                (Dresden/Nuremberg = 3 days because they are more remote)
# income       = general income level — affects order size
# heavy_pct    = probability that a customer in this city works in heavy industry
#                (Stuttgart = 45% because of the automotive/manufacturing sector)

cities = {
    'Hamburg':   {'weight':0.20, 'delivery_days':1, 'income':'high',   'heavy_pct':0.40},
    'Berlin':    {'weight':0.18, 'delivery_days':1, 'income':'high',   'heavy_pct':0.30},
    'Munich':    {'weight':0.16, 'delivery_days':1, 'income':'high',   'heavy_pct':0.35},
    'Stuttgart': {'weight':0.12, 'delivery_days':2, 'income':'high',   'heavy_pct':0.45},
    'Frankfurt': {'weight':0.12, 'delivery_days':1, 'income':'high',   'heavy_pct':0.28},
    'Cologne':   {'weight':0.10, 'delivery_days':2, 'income':'medium', 'heavy_pct':0.32},
    'Dresden':   {'weight':0.07, 'delivery_days':3, 'income':'medium', 'heavy_pct':0.38},
    'Nuremberg': {'weight':0.05, 'delivery_days':3, 'income':'medium', 'heavy_pct':0.42},
}
# NOTE: weights must sum to 1.0 — they represent the probability distribution

# ── 1B: TECHNICIAN LEVELS ─────────────────────────────────────────────────────
# basket_size     = average number of items per order
#                   (Master Mechanic = 5.3 because they buy full maintenance kits)
# avg_order_value = average total value of an order in euros
#                   (Junior = €210, Maintenance Engineer = €960)
# These values reflect real MRO industry benchmarks

tech_levels = {
    'Junior Technician':    {'weight':0.30, 'basket_size':1.9, 'avg_order_value':210},
    'Senior Technician':    {'weight':0.45, 'basket_size':3.4, 'avg_order_value':480},
    'Maintenance Engineer': {'weight':0.25, 'basket_size':5.3, 'avg_order_value':960},
}

# ── 1C: WORK SITUATIONS ───────────────────────────────────────────────────────
# order_value_mult = multiplier applied to order value
#                    (Facility Manager = 1.45x because they buy for whole facilities)
#                    (Freelance = 0.80x because they buy for one job at a time)
# retention        = probability of re-ordering (loyalty score)
#                    (Facility Manager = 88% retention — they have a long-term need)

work_situations = {
    'Freelance':        {'weight':0.30, 'order_value_mult':0.80, 'retention':0.62},
    'Company Employee': {'weight':0.35, 'order_value_mult':0.95, 'retention':0.72},
    'Facility Manager': {'weight':0.35, 'order_value_mult':1.45, 'retention':0.88},
}

# ── 1D: INDUSTRY TYPES ────────────────────────────────────────────────────────
# part_price_mult = Heavy Industry parts cost more than Light Industry
#                   (hydraulic seals for a steel plant vs a bakery)

industry_types = {
    'Light Industry': {'weight':0.60, 'part_price_mult':0.80},
    'Heavy Industry': {'weight':0.40, 'part_price_mult':1.30},
}

# ── 1E: PRODUCT CATEGORIES ────────────────────────────────────────────────────
# margin       = gross profit margin (Fasteners = 42% because they are commodity)
# avg_price    = base unit price in euros
# level_req    = minimum technician level needed to buy this product
#                (Hydraulic Parts require Maintenance Engineer — complex installation)
# industry_specific = True means the product only fits certain industry types

categories = {
    'Hand Tools':             {'margin':0.38, 'avg_price':120, 'level_req':'Junior Technician',    'industry_specific':False},
    'Power Tools':            {'margin':0.32, 'avg_price':380, 'level_req':'Senior Technician',    'industry_specific':False},
    'Pneumatic Tools':        {'margin':0.30, 'avg_price':290, 'level_req':'Senior Technician',    'industry_specific':True},
    'Fasteners & Fixings':    {'margin':0.42, 'avg_price':75,  'level_req':'Junior Technician',    'industry_specific':False},
    'Lubricants & Fluids':    {'margin':0.40, 'avg_price':90,  'level_req':'Junior Technician',    'industry_specific':False},
    'Safety Equipment':       {'margin':0.35, 'avg_price':160, 'level_req':'Junior Technician',    'industry_specific':False},
    'Electrical Components':  {'margin':0.28, 'avg_price':340, 'level_req':'Maintenance Engineer', 'industry_specific':True},
    'Hydraulic Parts':        {'margin':0.26, 'avg_price':560, 'level_req':'Maintenance Engineer', 'industry_specific':True},
    'Diagnostic Equipment':   {'margin':0.22, 'avg_price':980, 'level_req':'Maintenance Engineer', 'industry_specific':False},
    'Cutting & Abrasives':    {'margin':0.36, 'avg_price':95,  'level_req':'Senior Technician',    'industry_specific':False},
}

# ── 1F: SUPPLIER COUNTRIES ────────────────────────────────────────────────────
# reliability = probability of delivering on time
#               (Germany = 94% — local, reliable logistics)
#               (China = 71% — long transit, customs delays)
# lead_days   = standard days from order to delivery
#               (Germany = 2 days, China = 18 days)

supplier_countries = {
    'Germany':     {'weight':0.40, 'reliability':0.94, 'lead_days':2},
    'China':       {'weight':0.25, 'reliability':0.71, 'lead_days':18},
    'Netherlands': {'weight':0.15, 'reliability':0.89, 'lead_days':3},
    'Poland':      {'weight':0.12, 'reliability':0.82, 'lead_days':5},
    'Italy':       {'weight':0.08, 'reliability':0.86, 'lead_days':7},
}

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — GENERATE CUSTOMERS TABLE
# 500 customers with realistic attributes based on the parameters above
# ══════════════════════════════════════════════════════════════════════════════

N_CUSTOMERS = 500
START_DATE  = datetime(2022, 1, 1)

# Extract lists and weights for random selection
city_names = list(cities.keys())
city_w     = [cities[c]['weight'] for c in city_names]

tech_names = list(tech_levels.keys())
tech_w     = [tech_levels[t]['weight'] for t in tech_names]

work_names = list(work_situations.keys())
work_w     = [work_situations[w]['weight'] for w in work_names]

customers = []
for i in range(N_CUSTOMERS):

    # Step 1: Randomly pick city, level, work situation
    # np.random.choice uses the weight arrays to create a weighted probability
    # e.g. Hamburg (weight 0.20) is 4x more likely than Nuremberg (weight 0.05)
    city  = np.random.choice(city_names, p=city_w)
    level = np.random.choice(tech_names,  p=tech_w)
    work  = np.random.choice(work_names,  p=work_w)

    # Step 2: Determine industry type
    # Base probability comes from city's heavy_pct
    # Adjusted upward for higher skill levels and Facility Managers
    # because they are more likely to work in industrial settings
    heavy_prob = cities[city]['heavy_pct']
    if level == 'Maintenance Engineer': heavy_prob += 0.10
    if work  == 'Facility Manager':     heavy_prob += 0.08
    heavy_prob = min(heavy_prob, 1.0)  # cap at 100%
    industry   = 'Heavy Industry' if np.random.random() < heavy_prob else 'Light Industry'

    # Step 3: Random registration date in first 6 months of 2022
    reg_date = START_DATE + timedelta(days=np.random.randint(0, 180))

    customers.append({
        'customer_id':       f'CUST-{str(i+1).zfill(4)}',
        'city':              city,
        'technician_level':  level,
        'work_situation':    work,
        'industry_type':     industry,
        'registration_date': reg_date.date(),
        'delivery_days_avg': cities[city]['delivery_days'],
    })

customers_df = pd.DataFrame(customers)
print(f"✅ Customers generated: {len(customers_df):,}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — GENERATE PRODUCTS TABLE
# 300 SKUs across 10 categories
# ══════════════════════════════════════════════════════════════════════════════

N_PRODUCTS = 300
cat_names  = list(categories.keys())

products = []
for i in range(N_PRODUCTS):
    cat  = np.random.choice(cat_names)  # random category
    meta = categories[cat]
    base = meta['avg_price']

    # Price varies around the base using normal distribution
    # Standard deviation = 30% of base price
    # Example: avg_price=380 → actual prices range roughly €180–€580
    unit_price = max(15, round(np.random.normal(base, base * 0.3), 2))

    products.append({
        'product_id':      f'SKU-{str(i+1).zfill(4)}',
        'category':        cat,
        # Industry compatibility — for industry-specific products,
        # randomly assign Light, Heavy, or Universal compatibility
        'industry_compatible': np.random.choice(
            ['Light Industry', 'Heavy Industry', 'Universal']
        ) if meta['industry_specific'] else 'Universal',
        'level_required':  meta['level_req'],
        'unit_price':      unit_price,
        'margin_pct':      meta['margin'],
        'is_critical':     1 if np.random.random() < 0.28 else 0,
        'min_order_qty':   np.random.choice([1, 2, 5, 10]),
    })

products_df = pd.DataFrame(products)
print(f"✅ Products generated: {len(products_df):,}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — GENERATE SUPPLIERS TABLE
# 30 suppliers across 5 countries
# ══════════════════════════════════════════════════════════════════════════════

N_SUPPLIERS   = 30
sup_countries = list(supplier_countries.keys())
sup_w         = [supplier_countries[c]['weight'] for c in sup_countries]

suppliers = []
for i in range(N_SUPPLIERS):
    country = np.random.choice(sup_countries, p=sup_w)
    meta    = supplier_countries[country]

    # Reliability varies slightly around the country average
    # German suppliers: avg 0.94 ± 0.07
    # Chinese suppliers: avg 0.71 ± 0.07
    reliability = round(
        min(1.0, max(0.5, np.random.normal(meta['reliability'], 0.07))), 2)

    suppliers.append({
        'supplier_id':       f'SUP-{str(i+1).zfill(3)}',
        'supplier_country':  country,
        'reliability_score': reliability,
        'avg_lead_days':     meta['lead_days'] + np.random.randint(-1, 4),
        'min_order_value':   np.random.choice([500, 1000, 2000, 5000]),
    })

suppliers_df = pd.DataFrame(suppliers)
print(f"✅ Suppliers generated: {len(suppliers_df):,}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — GENERATE CUSTOMER ORDERS TABLE
# 20,000 orders — each one goes through a multi-step realistic process
# ══════════════════════════════════════════════════════════════════════════════

N_ORDERS = 20000
orders   = []

for i in range(N_ORDERS):

    # Step 1: Pick a random customer
    cust      = customers_df.sample(1).iloc[0]
    tech_meta = tech_levels[cust['technician_level']]
    work_meta = work_situations[cust['work_situation']]
    ind_meta  = industry_types[cust['industry_type']]

    # Step 2: Calculate basket size
    # Based on technician level AND work situation multiplier
    # Normal distribution centered on the expected basket size
    # e.g. Maintenance Engineer (5.3) × Facility Manager (1.45) → large baskets
    basket_size = max(1, int(np.random.normal(
        tech_meta['basket_size'] * work_meta['order_value_mult'], 1.5)))

    # Step 3: Random order date across 2 years
    order_date = START_DATE + timedelta(days=np.random.uniform(0, 730))

    # Step 4: Filter products the customer can actually buy
    # A Junior Technician cannot order Hydraulic Parts (requires Engineer level)
    # Also filter by industry compatibility
    level_order    = ['Junior Technician', 'Senior Technician', 'Maintenance Engineer']
    level_idx      = level_order.index(cust['technician_level'])
    eligible_prods = products_df[
        products_df['level_required'].isin(level_order[:level_idx+1])]
    compat_prods   = eligible_prods[
        (eligible_prods['industry_compatible'] == cust['industry_type']) |
        (eligible_prods['industry_compatible'] == 'Universal')]
    if len(compat_prods) == 0:
        compat_prods = eligible_prods  # fallback if no compatible products

    # Step 5: Sample products for this order
    n_items        = min(basket_size, len(compat_prods))
    order_products = compat_prods.sample(n_items, replace=True)

    # Step 6: Calculate order value
    # Each product: price × random quantity (1–4 units)
    # Then multiply by industry price factor
    base_value  = (order_products['unit_price'] *
                   np.random.randint(1, 5, n_items)).sum()
    order_value = round(base_value * ind_meta['part_price_mult'], 2)

    # Step 7: Calculate delivery timing
    # Promised days = city standard + small random variation
    # Delay = exponential distribution — most orders (56%) arrive on time
    # Exponential chosen because delays have a "long tail" — rare extreme delays
    promised_days = cities[cust['city']]['delivery_days'] + np.random.randint(0, 2)
    delay         = max(0, int(np.random.exponential(1.2)))
    actual_days   = promised_days + delay

    orders.append({
        'order_id':         f'ORD-{str(i+1).zfill(6)}',
        'customer_id':      cust['customer_id'],
        'city':             cust['city'],
        'technician_level': cust['technician_level'],
        'work_situation':   cust['work_situation'],
        'industry_type':    cust['industry_type'],
        'order_date':       order_date.date(),
        'order_month':      order_date.strftime('%Y-%m'),
        'order_quarter':    f"{order_date.year}Q{(order_date.month-1)//3+1}",
        'order_year':       order_date.year,
        'basket_size':      n_items,
        'order_value':      order_value,
        'gross_profit':     round(order_value * 0.32, 2),  # 32% margin assumption
        'promised_days':    promised_days,
        'actual_days':      actual_days,
        'delay_days':       delay,
        'on_time':          1 if delay == 0 else 0,       # 1 = on time, 0 = late
        'on_time_label':    'On Time' if delay == 0 else 'Late',
        # Return rate: 5.5% probability — realistic for B2B MRO
        'is_returned':      1 if np.random.random() < 0.055 else 0,
        'return_reason':    np.random.choice([
            'Wrong item ordered', 'Defective product',
            'Compatibility issue', 'Over-ordered', 'No reason given'
        ]) if np.random.random() < 0.055 else 'Not returned',
    })

orders_df = pd.DataFrame(orders)
print(f"✅ Customer orders generated: {len(orders_df):,}")
print(f"   On-time rate: {orders_df['on_time'].mean()*100:.1f}%")
print(f"   Avg basket:   {orders_df['basket_size'].mean():.2f}")
print(f"   Avg order:    €{orders_df['order_value'].mean():,.0f}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — GENERATE SUPPLIER ORDERS TABLE
# 15,000 procurement orders from suppliers
# ══════════════════════════════════════════════════════════════════════════════

sup_orders = []
for i in range(15000):

    # Step 1: Pick a random supplier and product
    sup        = suppliers_df.sample(1).iloc[0]
    prod       = products_df.sample(1).iloc[0]
    order_date = START_DATE + timedelta(days=np.random.uniform(0, 730))

    # Step 2: Calculate actual lead time
    # Base: supplier's average lead days
    # Delay multiplier: unreliable suppliers get exponentially longer delays
    # Formula: actual = base × (1 + (1 - reliability) × random_exponential)
    # Example: China supplier (reliability 0.71):
    #   multiplier = 1 + 0.29 × exp(1.0) ≈ 1.79 on average
    #   actual lead = 18 × 1.79 ≈ 32 days when delayed
    base_lead   = sup['avg_lead_days']
    delay_mult  = 1 + (1 - sup['reliability_score']) * np.random.exponential(1.0)
    actual_lead = max(1, int(base_lead * delay_mult))
    promised    = base_lead + 2   # promise 2 days buffer

    qty       = np.random.randint(10, 200)
    order_val = round(qty * prod['unit_price'] * 0.68, 2)  # 68% = cost price (32% margin)

    sup_orders.append({
        'sup_order_id':       f'PO-{str(i+1).zfill(6)}',
        'supplier_id':        sup['supplier_id'],
        'supplier_country':   sup['supplier_country'],
        'product_id':         prod['product_id'],
        'category':           prod['category'],
        'order_date':         order_date.date(),
        'order_month':        order_date.strftime('%Y-%m'),
        'order_quarter':      f"{order_date.year}Q{(order_date.month-1)//3+1}",
        'quantity':           qty,
        'order_value':        order_val,
        'promised_lead_days': promised,
        'actual_lead_days':   actual_lead,
        'lead_delay_days':    max(0, actual_lead - promised),
        'on_time':            1 if actual_lead <= promised else 0,
        'reliability_score':  sup['reliability_score'],
    })

sup_orders_df = pd.DataFrame(sup_orders)
print(f"✅ Supplier orders generated: {len(sup_orders_df):,}")
print(f"   Supplier on-time rate: {sup_orders_df['on_time'].mean()*100:.1f}%")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — SAVE ALL FILES
# ══════════════════════════════════════════════════════════════════════════════

import os
output_dir = os.path.dirname(os.path.abspath(__file__))

customers_df.to_csv(f'{output_dir}/customers.csv',      index=False)
products_df.to_csv(f'{output_dir}/products.csv',        index=False)
suppliers_df.to_csv(f'{output_dir}/suppliers.csv',      index=False)
orders_df.to_csv(f'{output_dir}/customer_orders.csv',   index=False)
sup_orders_df.to_csv(f'{output_dir}/supplier_orders.csv', index=False)

print(f"\n✅ All 5 CSV files saved to: {output_dir}")
print(f"\n{'='*55}")
print(f"  DATASET SUMMARY")
print(f"{'='*55}")
print(f"  Customers        : {len(customers_df):>8,}")
print(f"  Products (SKUs)  : {len(products_df):>8,}")
print(f"  Suppliers        : {len(suppliers_df):>8,}")
print(f"  Customer orders  : {len(orders_df):>8,}")
print(f"  Supplier orders  : {len(sup_orders_df):>8,}")
print(f"  Total revenue    : €{orders_df['order_value'].sum():>12,.0f}")
print(f"  Gross profit     : €{orders_df['gross_profit'].sum():>12,.0f}")
print(f"  Cust. on-time    : {orders_df['on_time'].mean()*100:>7.1f}%")
print(f"  Sup. on-time     : {sup_orders_df['on_time'].mean()*100:>7.1f}%")
print(f"{'='*55}")

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW TO EXPLAIN THIS IN AN INTERVIEW:

"This dataset was generated using a business simulation
script. I defined the real parameters of a B2B MRO
business — city distributions, technician skill levels,
supplier reliability by country, and industry types —
and used Python to generate 20,000 realistic orders that
follow those rules. This is called synthetic data and is
standard practice in data science when real operational
data is confidential. The approach mirrors what I used in
my Master's thesis at the University of Europe, Hamburg."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
