# Every Unit Matters 🏥

A **Dynamic Programming (DP) solution** for optimizing **medical supply inventory** over a T-months horizon. This tool computes the **optimal ordering schedule** to minimize total costs while respecting storage limits and handling emergency orders.

---

## Overview

Hospitals must balance **ordering enough to avoid shortages** while avoiding **overstocking** and excessive holding costs.

This project addresses the **Single-Item Inventory Optimization Problem**:

* **Finite Horizon:** 12 months
* **Deterministic Demand:** Known demand per month
* **Storage Constraints:** Maximum inventory per month
* **Emergency Orders:** Cover shortages at higher cost

> Key question: *“How much should we order each month to minimize total cost while avoiding shortages?”*

---

## Our Approach 😎

We used **Dynamic Programming** to explore all feasible inventory decisions while tracking:

* **Inventory at the start of each month**
* **Regular orders**
* **End-of-month inventory**
* **Emergency orders, if any**

**DP Principle:** The optimal cost at any month depends on the **best possible decisions in future months**, giving **optimal substructure**.

We also implemented a **Greedy baseline** that orders exactly the current demand each month (ignores future costs).

---

## System Model & Cost Function $

For each month (t):

1. **Regular Order Cost:** (C_{\text{order}} = c_\text{fixed} + c_\text{unit} \times q)
2. **Storage Cost:** (C_{\text{holding}} = c_\text{storage} \times I_\text{end})
3. **Emergency Cost:** (C_{\text{emergency}} = c_\text{emergency_fixed} + c_\text{emergency_unit} \times \text{shortage})

**Inventory Dynamics:**

[
I_{t+1} = \max(0, I_t + q_t - D_t)
]

**Objective:** Minimize total cost over all months.

---

## Parameters & Inputs 

| Parameter                | Description                     |
| ------------------------ | ------------------------------- |
| **T**                    | Number of periods (months)      |
| **Demand**               | List of monthly demand values   |
| **Initial Inventory**    | Stock on hand at month 0        |
| **Max Storage**          | Maximum inventory allowed       |
| **Order Fixed Cost**     | Fixed fee per order             |
| **Order Unit Cost**      | Variable cost per unit          |
| **Storage Cost / Unit**  | Cost per unit stored per month  |
| **Emergency Fixed Cost** | Fixed cost for emergency orders |
| **Emergency Unit Cost**  | Unit cost for emergency orders  |

---

## How to Run 🤔

1. Clone/download the project.
2. Make sure **Python 3.11.2** is installed or any version that is **3.8+** .
3. Install dependencies:

```bash
pip install numpy matplotlib tkinter
```

4. Run the script:

```bash
python main.py
```

5. The solver will return:

   * Optimal DP schedule
   * Greedy baseline schedule
   * Total costs for both
   * you can find multiple tabs as below where you can analyze and detect patterns & view behavior

---

## Test Cases & Edge Scenarios 💀

Try these to validate behavior:

1. **Zero Demand:** All months = 0 → no orders, no cost
2. **Demand Exceeds Max Capacity:** DP places max regular order + emergency orders
3. **Initial Inventory > Max Storage:** Algorithm should cap inventory
4. **Extremely Low Max Capacity:** Frequent emergency orders
5. **High Order Fixed Cost:** DP batches orders to reduce frequency
6. **High Emergency Cost:** DP anticipates spikes, avoids emergencies

> Placeholder: Add figures showing DP vs. Greedy for these cases
> ![DP vs Greedy Placeholder](./figures/dp_vs_greedy.png)

---

## Output & Visualization 🎨

Each schedule includes:

| Column    | Meaning                                    |
| --------- | ------------------------------------------ |
| Start     | Inventory at start of month                |
| Order     | Regular order placed                       |
| Emergency | Units ordered immediately at premium price |
| End       | Inventory at end of month                  |
| Cost      | Total cost this month                      |

> Placeholder: Inventory trajectory plot
> ![Inventory Trajectory Placeholder](./figures/inventory_trajectory.png)

> Placeholder: Cost breakdown plot
> ![Cost Breakdown Placeholder](./figures/cost_breakdown.png)

---

## Performance Notes 📋

* Complexity: (O(T \cdot N \cdot U)) where

  * (T) = periods, (N) = max inventory states, (U) = feasible order quantities
* Tractable for moderate storage and periods
* Exhaustive DP ensures **globally optimal policy**

---

## 🤝 Contributing

Educational project for **Operations Research and Healthcare Inventory Optimization**.

* Test new demand sequences
* Modify costs and constraints
* Compare DP with other heuristics

---
## Acknowledgement 🙏🏻
* I would like to thank the whole team for their great work:
Thanks to @Mohamed0Ehab & @WardSalkini and @AboSaree for building the core functionalities for this project, brainstorming different structures, late-night work that brought this thing to reality
Special Thanks to my mate @Kareem-Taha-05 who always viewed things at micro-scale, whenever we are stuck he was the guy with the skillset to help

Finally, I would like to thank Prof. Eman Ayman & Our TA Eng. Yara El-Shamy for Supervising this project and their Mentorship Throughout the Course. 

---

## 📄 License

Open Source

