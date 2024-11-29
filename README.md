# 💰 Economical Reverse ETL Project

A lightweight reverse ETL solution that extracts data from your data warehouse, performs transformations, and loads it back into PostgreSQL for optimized querying.

## 📋 Overview

This project enables cost-effective reverse ETL by moving data from your data warehouse back into operational databases. The solution is built using serverless and managed AWS services combined with high-performance data processing.

## 🛠️ Tech Stack

- **AWS Services**
  - 🖥️ EC2 (Spot Instances) - Hosts the core ETL processes
  - ⚡ Lambda - Triggers spot instances and cleanup
  - ⏰ EventBridge - Orchestrates the ETL workflow
  - 📦 S3 - Stores ETL code and intermediate data
  - 📨 SNS - Handles ETL completion notifications
  - 🏭 Redshift - Source data warehouse
- **Infrastructure as Code**
  - 🚀 AWS CDK - Defines and deploys AWS resources
  - ⚙️ Environment configs (dev/prod)
- **Databases**
  - 🐘 PostgreSQL - Target operational database
- **Processing**
  - 🐻‍❄️ Polars - High performance DataFrame library for transformations

## 🏗️ Architecture

1. ⏰ EventBridge triggers the trigger-etl Lambda function on schedule
2. ⚡ Lambda function launches EC2 spot instance with ETL code from S3
3. 📤 Spot instance extracts data from Redshift warehouse
4. 🔄 Transformations are performed using Polars DataFrame library
5. 📥 Final transformed data is loaded into PostgreSQL
6. 📨 ETL process sends completion notification to SNS topic
7. 🧹 Cleanup Lambda receives SNS notification and terminates spot instance