# Package Return Tracker

## What is This Project
Package Return Tracker is a machine learning powered tool that helps customers track their package return deadlines, predicts which packages are likely to be returned, and automatically reminds them before the return window closes so they never get stuck with an item they wanted to send back.

## The Problem
When a package arrives, customers intend to decide whether to keep or return it but set it aside and forget. The return window quietly closes and they are stuck with the item. There is no system that watches their deliveries, predicts which ones are at risk, and reminds them at the right time. Retailers also lose billions annually because customers miss return windows and then raise disputes, chargebacks, and complaints instead.

## The Solution
Package Return Tracker solves this in three steps. First it predicts which delivered packages are likely to be returned using a machine learning model trained on order data. Second it reads any return reason the customer types and automatically categorizes it using an NLP model. Third it tracks the return deadline for every order in a database and fires reminders before the window closes, walking the customer through the return process.

## Tech Stack
- Python 3.12 — core language for all scripts, models, and automation
- pandas — loading, cleaning, and transforming order data
- scikit-learn — model training, TF-IDF vectorizer, preprocessing, evaluation metrics
- XGBoost — gradient boosting classifier for return likelihood prediction
- matplotlib and seaborn — charts for EDA, confusion matrix, feature importance
- SQLite and sqlite3 — lightweight database storing orders, return windows, reasons, and notifications
- pickle — saving and loading trained models
- Jupyter Notebook — environment for EDA, model training, and evaluation

## How it Works — Step by Step
Step 1 — Data: 3000 synthetic orders are generated with features like category, price, discount percentage, vendor, and whether multiple sizes were ordered. Return likelihood is made to depend realistically on these features.
Step 2 — EDA: charts are produced showing overall return rate, return rate by category, impact of ordering multiple sizes, and price distribution for returned vs kept orders.
Step 3 — ML Model 1: three classifiers are trained and compared — Logistic Regression as a baseline, Random Forest, and XGBoost. The best model is selected by ROC-AUC score and saved.
Step 4 — ML Model 2: 150 labelled return reason phrases are used to train a TF-IDF plus Logistic Regression pipeline that reads free text and outputs one of five categories — size_issue, damaged, changed_mind, not_as_described, price.
Step 5 — Database: a SQLite database stores all orders, return windows, classified reasons, and notifications across 4 linked tables.
Step 6 — Automation: run_reminders.py runs daily, scores all delivered orders through both models, fires reminders for likely returns, sends urgent alerts for closing windows, and auto-categorizes any unclassified return reasons.

## How to Run
1. pip install -r requirements.txt
2. py data/generate_data.py
3. py db/init_db.py
4. Open notebooks/return_tracker.ipynb and run all cells
5. py alerts/run_reminders.py

## Folder Structure
Show the full folder tree of the project

## What I Wanted to Achieve
- Build a real end to end machine learning project that goes from raw data to a working automated system
- Learn and apply two types of ML — tabular classification and NLP text classification in one project
- Understand reverse logistics as a domain and build something relevant to it
- Practice SQL database design with linked tables and foreign keys
- Show that a data science project is not just a notebook but includes a database layer and an automation layer that runs on a schedule




