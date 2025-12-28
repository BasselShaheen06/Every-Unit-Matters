# Every Unit Matters

A Dynamic Programming (DP) solution for optimizing medical supply inventory over a 12-month planning horizon. This tool determines the optimal ordering schedule to minimize total costs while handling complex constraints like delivery lead times and storage capacity.

## 📋 Project Overview

This application solves the **Single-Item Dynamic Lot Sizing Problem** with the following characteristics:
* **Deterministic Demand:** Future demand is known for the 12-month period.
* **3-Month Lead Time:** Orders placed in month `t` arrive in month `t+3`.
* **Storage Constraints:** Warehouse capacity is strictly limited.
* **Emergency Orders:** Immediate fulfillment options are available (at a premium) if shortages occur.

The goal is to answer the question: *"How much should we order today to satisfy future demand at the lowest possible cost?"*

## 🚀 Key Features

* **Recursive Dynamic Programming:** Uses memoization (`lru_cache`) to efficiently solve high-dimensional state spaces.
* **Lead Time Handling:** Correctly models "pipeline inventory" (goods in transit) to ensure realistic planning.
* **Interactive GUI:** Built with `tkinter` for easy input adjustment and visualization.
* **Data Visualization:** Plots for Inventory Levels, Demand vs. Supply, and Cost Breakdown.
* **Detailed Backtracking:** Provides a month-by-month table showing exactly what happens at every step (Orders, Arrivals, Emergencies, and End-of-Month Stock).

## ⚙️ Prerequisites

You need **Python 3.x** installed. The project relies on the following standard libraries:

* `tkinter` (usually comes pre-installed with Python)
* `numpy`
* `matplotlib`

To install the dependencies:
```bash
pip install numpy matplotlib
```

## 🏃 How to Run

1.  Download the `optimum_Cost.py` file.
2.  Run the script via terminal or command prompt:

```bash
python optimum_Cost.py
```

3.  The GUI window will open.
4.  Adjust inputs (optional) and click **"Run Optimization"**.
5.  Wait for the solver to finish (approx. 30-60 seconds for complex states).

## 🧠 The Mathematical Model

The solver uses a state-based recursion:

$$V(t, I, p_1, p_2, p_3)$$

Where:
* **$t$**: Current month (0-12).
* **$I$**: Current on-hand inventory.
* **$p_1, p_2, p_3$**: Pipeline inventory arriving in 1, 2, and 3 months respectively.

### Cost Function
For every month, the total cost is:
$$Cost = C_{ordering}(q) + C_{holding}(I_{end}) + C_{emergency}(Shortage) + V(t+1, ...)$$

## 📖 Usage Guide & Inputs

### Input Fields
| Parameter | Description |
| :--- | :--- |
| **Ordering Costs** | Fixed fee per order + variable cost per unit. |
| **Storage Cost** | Cost to hold one unit overnight. |
| **Emergency Costs** | High premium costs for immediate, same-day delivery (used when stock runs out). |
| **Max Storage** | Maximum capacity of the warehouse. **Note:** This limits *End-of-Month* inventory, not receiving capacity. |
| **Demand** | Comma-separated list of demand for 12 months. |
| **Initial Inventory** | Stock on hand at the start of Month 0. |

### Understanding the Output Table
* **Start:** Total inventory available at the beginning of the month (Previous Inventory + Arriving Orders). *Note: This can exceed Max Storage because it includes goods that are immediately sold.*
* **Order:** Quantity ordered *now*. Due to lead time, this arrives in 3 months.
* **Emergency:** Units bought immediately at a premium price to cover shortages.
* **End:** Inventory remaining overnight. This is strictly capped at **Max Storage**.

## ⚠️ Performance Note

Because this model accounts for a **3-month lead time**, the complexity is high (5-dimensional state space).
* **Standard Run:** With Max Storage ~30, execution takes **30-60 seconds**.
* **Fast Run:** To test logic quickly, reduce Max Storage to **15** and Demand values to single digits.

## 🤝 Contributing
This project is an educational tool for Operations Research and Industrial Engineering concepts. Feel free to fork and experiment with different cost functions or stochastic demand.

## 📄 License
Open Source.
