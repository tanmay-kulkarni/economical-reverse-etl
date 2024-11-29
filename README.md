# Economical Reverse ETL Project

A lightweight reverse ETL solution that extracts data from your data warehouse, performs transformations, and loads it back into PostgreSQL for optimized querying.

## Overview

This project enables cost-effective reverse ETL by moving data from your data warehouse back into operational databases. The solution is built using serverless and managed AWS services combined with high-performance data processing.

## Tech Stack

- **AWS Services**
  - EC2 (Spot Instances) - Hosts the core ETL processes
  - Lambda - Handles event-driven transformations
  - EventBridge - Orchestrates the ETL workflow
  - S3 - Stores intermediate data
  - Redshift - Source data warehouse
- **Databases**
  - PostgreSQL - Target operational database
- **Processing**
  - Polars - High performance DataFrame library for transformations

## Architecture

1. Data is extracted from Redshift data warehouse
2. Transformations are performed using Polars DataFrame library
3. Processed data is staged in S3
4. Final transformed data is loaded into PostgreSQL
5. EventBridge manages the scheduling and orchestration