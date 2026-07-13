# Wind-Turbine-Reliability-Analytics-and-Reporting-Automation-Pipeline
## Overview
Wind farm operators generate large volumes of operational data from SCADA systems, downtime logs, issue libraries, and maintenance records. Transforming these datasets into actionable insights is essential for improving reliability, reducing downtime, and optimizing maintenance strategies.

This project provides an automated analytics pipeline that:
  - Integrates multiple operational datasets
  - Cleans and standardizes asset data
  - Maps downtime events to known failure modes
  - Calculates reliability KPIs
  - Identifies the most critical recurring issues
  - Evaluates intervention effectiveness
  - Prioritizes wind farms based on reliability performance
  - Generates reporting-ready datasets for Power BI or other BI tools
## Key Features
  - Automated multi-source data ingestion
  - Data cleaning and preprocessing
  - Downtime event processing
  - Issue and solution mapping
  - Farm-level KPI generation
  - Issue-level reliability analysis
  - Intervention Rate calculation
  - MTBI (Mean Time Between Interventions)
  - MTTR (Mean Time To Repair)
  - FTFR (First Time Fix Rate)
  - Target vs Actual comparison
  - Automated status comments
  - Top issue identification per wind farm
  - Priority score calculation
  - Materialized reporting dataset generation

## Project Workflow
Configuration
      │
      ▼
Load Input Data
      │
      ▼
Data Cleaning & Standardization
      │
      ▼
Feature Engineering
      │
      ▼
Issue & Solution Mapping
      │
      ▼
Downtime Processing
      │
      ▼
Farm Level Aggregation
      │
      ▼
Reliability KPI Calculation
      │
      ▼
Issue Level Analysis
      │
      ▼
Solution Effectiveness Analysis
      │
      ▼
Top N Issue Identification
      │
      ▼
Priority Score Calculation
      │
      ▼
Reporting Dataset Generation

## Repository Structure
.
├── config/
│   └── config.yaml
│
├── data/
│   ├── input/
│   └── output/
│
├── src/
│   ├── data_ingestion/
│   ├── data_processing/
│   ├── reporting/
│   └── utils/
│
├── main.py
├── requirements.txt
└── README.md

## Input Datasets

The pipeline uses the following operational datasets.

Dataset	Purpose
<img width="716" height="241" alt="image" src="https://github.com/user-attachments/assets/721a97bc-b56d-4ac8-b7f3-2fe004576ea5" />

Dataset locations are configured through:

config/config.yaml
