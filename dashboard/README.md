# Power BI Dashboard

The Power BI dashboard provides an interactive view of the job market dataset.

## Dashboard Pages

### 1. Job Market Overview
- Total jobs
- Companies
- Locations
- Jobs with salary information
- Jobs by city
- Jobs by source

### 2. Skills & Hiring Demand
- Jobs with detected skills
- Unique skills
- Top skills
- Skill categories
- Skills by job category

### 3. Salary & Experience
- Average salary
- Median salary
- Jobs with salary information
- Salary distribution by salary band
- Median salary by city

## Data Source

The dashboard connects directly to the PostgreSQL `analytics` schema.

Main analytical view:

`analytics.job_market_features`
