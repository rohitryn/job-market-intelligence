# Job Market Intelligence & Salary Prediction

An end-to-end data analytics and machine learning project that collects job-market data, cleans and transforms it, stores it in PostgreSQL, extracts skills using NLP-based techniques, analyzes hiring and salary trends, and predicts salary using machine learning.

## Project Objective

The objective of this project is to build a job-market intelligence system that answers questions such as:

- Which skills are most in demand?
- Which companies are hiring the most?
- Which locations have the highest hiring demand?
- How do salaries vary by location, experience and skills?
- Can job characteristics be used to estimate salary?

## Architecture

```text
Job Websites / APIs
        ↓
Data Collection
        ↓
Python ETL & Cleaning
        ↓
Skill & Experience Extraction
        ↓
PostgreSQL
        ↓
SQL Analysis
        ↓
Machine Learning
        ↓
Power BI Dashboard
