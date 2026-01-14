# Rotman Interactive Trader – Algorithmic Market Making (ALGO 2)

This project is a **basic algorithmic trading strategy** developed for the **Rotman Interactive Trader (RIT)** simulator, specifically for the **Algorithmic Market Making (ALGO 2) case**.

**Case Description**:  
**Case Description**:  
[Algorithmic Market Making Case Brief (ALGO 2)](https://rotmanfrtl.github.io/RIT%20-%20Case%20Brief%20-%20ALGO2%20-%20Algorithmic%20Market%20Making.pdf)

**Rotman Interactive Trader Platform**:  
[Rotman Interactive Trader](https://www.rotman.utoronto.ca/faculty-and-research/education-labs/bmo-financial-group-finance-research-and-trading-lab/rit-market-simulator/)

---

## Objective of the Project

The goal of this project is to implement a **baseline market making algorithm** that continuously and automatically provides liquidity to the market by submitting **paired bid and ask orders** on a single stock.

The algorithm aims to:
- Capture the **bid–ask spread**
- Maintain a **balanced inventory**
- Limit excessive risk exposure
- Operate continuously throughout the trading session

This project focuses on **strategy logic and risk control**, rather than maximizing profitability in all market conditions.

---

## How the Code Works

### Case Timing Management
- The algorithm runs only while the case is active  
- Trading logic is executed continuously during the simulation window  
- No orders are submitted outside the valid case timeframe  

---

### Continuous Market Making Logic

At each iteration, the algorithm:

1. **Checks open orders**
   - If no orders are present, it submits a **pair of limit orders**
   - If only one order is present, all open orders are cancelled and reset

2. **Quotes the market**
   - A BUY limit order is placed below the reference price
   - A SELL limit order is placed above the reference price
   - The distance from the reference price is determined by a fixed spread

3. **Maintains market presence**
   - The algorithm ensures that it always has **both a bid and an ask** in the order book

---

### Inventory and Risk Management

The algorithm continuously monitors its position:

- A **preferred inventory range** is defined
- If inventory grows beyond this range:
  - The algorithm attempts to **close positions at a profit**
  - VWAP is compared with current best bid or ask prices
- If inventory exceeds a hard risk limit:
  - Market orders are used to **forcefully reduce exposure**

This ensures that the algorithm does not accumulate excessive directional risk.

---

## Limitations & Improvements

**Current limitations**
- Fixed bid–ask spread
- No dynamic inventory skewing
- Pricing based on last best bid and ask 
- Performance may degrade in trending or highly volatile markets

These limitations are intentional and reflect the role of this algorithm as a **baseline implementation**.

---

## Language Used

- **Python**

---

## Final Notes

This project demonstrates:
- A practical implementation of **market making mechanics**
- Understanding of **order book dynamics**
- Awareness of **inventory risk and execution constraints**
