# Media Industry Recruitment Data Analytics Platform (GoGoJob)

## 1. Project Overview

This project focuses on recruitment data for media and general operations roles, building an end-to-end application covering **data cleaning → database governance → model analysis → visualized decision-making**.

The system is designed to achieve the following objectives:

- Standardize multi-source recruitment data to ensure consistent statistical definitions;
- Build maintainable data assets in MySQL and avoid direct file access from the front end;
- Provide salary prediction and job matching capabilities for jobseekers;
- Deliver insights across dimensions such as region, education, experience, and company size through visual dashboards.

---

## 2. Core Features

- **One-time Data Cleaning Script**:
  - Province/city/region normalization  
  - Salary parsing  
  - Job title standardization  
  - Benefits extraction  
  - Structured parsing of job descriptions

- **SQL-based Data Services**:
  - All front-end charts and models are powered exclusively by MySQL queries

- **Salary Prediction**:
  - Hybrid output combining rule-based statistical fallback and machine learning models

- **Job Matching**:
  - Strong constraints on job category
  - Multi-dimensional scoring across location, salary, and seniority

- **Salary Heatmap**:
  - Province-level heatmap
  - Click-through interaction to city-level and job-level details

- **Enhanced Job Category Pages**:
  - Top 10 job listings added to each category page to reduce visual blank space

- **Cross-Job Comparison**:
  - Compare two different combinations of *job category + city*
  - Direct comparison of salary minimums, maximums, and averages

- **Navigation Grouping Enhancements**:
  - Segmented navigation: **POPULAR JOBS / VISUAL MAP / DATA ANALYSIS**

- **Top Avatar Menu**:
  - System management and logout moved to the top-right admin avatar menu
  - “Admin” label added for role clarity

- **Admin Info Bar**:
  - Avatar, text, and menu unified within a light-colored top bar for visual consistency

- **Back-office Management**:
  - User management
  - Initialization wizard
  - Manual data reload support

---

## 3. Technology Stack

### Front-End

- HTML5 + Jinja2
- CSS3 + Bootstrap
- JavaScript + Axios + ECharts

### Back-End

- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-Login

### Data & Modeling

- MySQL 8
- Pandas / NumPy
- scikit-learn (regression, feature vectorization, similarity computation)
- pypinyin (pinyin-based sorting)

---

## 4. Data Pipeline

- Raw recruitment files are stored in `raw_data/`;
- Run `clean_recruitment_data.py` to generate `clean_data/all_jobs_cleaned.csv`;
- Visit `/bootstrap` to fully import the cleaned CSV into the MySQL `jobs` table;
- Backend APIs provide statistical results and model inputs via SQL queries;
- Front-end pages interact with APIs for rendering and user interaction.

---

## 5. Project Structure
```text
GoGoJob/
├─ app/
│  ├─ routes/
│  │  ├─ auth.py                    # Login, Logout, User Management
│  │  └─ main.py                    # Page Routing + Data API
│  ├─ services/
│  │  ├─ analytics.py               # Statistics, prediction, and matching core logic
│  │  ├─ data_loader.py             # CSV -> SQL import
│  │  ├─ job_title.py               # Job Standardization Rules
│  │  └─ security.py                # Permissions and password policies
│  ├─ templates/
│  │  ├─ base.html                  # Site Layout and Navigation
│  │  ├─ login.html                 # Login page
│  │  ├─ dashboard.html             # Homepage
│  │  ├─ category.html              # Category Analysis Page
│  │  ├─ map.html                   # Salary heatmap
│  │  ├─ predict.html               # Salary forecast page
│  │  ├─ match.html                 # Job matching page
│  │  ├─ job_detail.html            # Job Details Page
│  │  ├─ compare.html               # Job Comparison Page
│  │  ├─ register.html              # New User Page
│  │  ├─ users.html                 # User Management Page
│  │  └─ setup.html                 # Initialize boot page
│  ├─ static/
│  │  ├─ css/main.css               # Global Styles
│  │  ├─ js/*.js                    # Page interaction scripts
│  │  └─ img/bgp.png        # Login background image
│  ├─ models.py                     # ORM Model
│  ├─ config.py                     # Configure database connection
│  └─ __init__.py                   # Application factory and initialization
├─ raw_data/                        # Raw data
├─ clean_data/                      # Cleaning results
├─ clean_recruitment_data.py        # Main script for initial data cleanup
├─ run.py                           # Service entry point
├─ requirements.txt                 # Dependency list
└─ docs/                            # Project Linkage and Steps Description
```

## 6. Database Design
### Jobs (Core Business Table)
- Primary key: `id`
- Source data identifier: `csv_id`
- Job information: `category`, `title`, `normalized_title`
- Region information: `province`, `city`, `region`
- Company information: `company_name`, `company_size`, `company_type`, `company_industry`
- Salary information: `min_salary`, `max_salary`, `avg_salary`
- Job requirements: `education`, `experience`
- Description information: `description`

### users (permission table)
- `id`, `username`, `password_hash`, `role`

## 7. Core Algorithm 
### 7.1 Salary Forecast
- **Statistical Priority Strategy**: Under the constraint of the same job category, backtrack layer by layer according to "province/city/education level/experience/scale", and give priority to using the quantile intervals of the same grouped samples;
- **Model backoff strategy:** When there are insufficient samples, use textual structural features as input to the regression model;
- **Model Selection**: Compare the validation set MAE among RandomForest, ExtraTrees, and GradientBoosting, and select the model with the lower error.
- **Output Items**: Minimum, Maximum, Mean, Confidence Score, Sample Size, Model Indicators.

### 7.2 Job Matching
- **Hard constraint**: Matching candidates are only drawn from the job categories selected by the user;
- **Multidimensional scoring**: City/province matching, salary range matching, education and experience matching, and scale matching;
- **Similarity Enhancement**: Calculate cosine similarity for structured feature vectors to enhance score differentiation;
- **Output Results**: Top 10 results and sub-item scores.

## 8. Application of Big Data Technology
- Batch processing and cleaning of multiple files, and field normalization;
- High-dimensional feature vectorization and model caching;
- Stratified rollback ensures interpretability for small samples;
SQL serves as a unified data service layer, supporting continuous incremental updates.

## 9. Installation and Operation
### 9.1 Environmental Requirements
- Python 3.10+
- MySQL 8.0+

### 9.2 Installation Steps
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a database:
   ```sql
   CREATE DATABASE gogojob CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
   ```
   - Open the app/config.py file in your project, find the "MySQL Configuration" section, and modify the following parameters to your local MySQL information:
     - MYSQL_PORT: Your MySQL port number (default 3306)
     - MYSQL_PASSWORD: Your MySQL root user password
     - Other parameters can be left at their default values unless otherwise specified.


3. Start the service:
   ```bash
   python run.py
   ```

4. Initial data import:
- Log in to access: `http://127.0.0.1:5000/bootstrap`

## 10. Project Features
- Open the app/config.py file in your project, find the "MySQL Configuration" section, and modify the following parameters to your local MySQL information:
- MYSQL_PORT: Your MySQL port number (default 3306)
- MYSQL_PASSWORD: Your MySQL root user password

- Other parameters can be left at their default values unless otherwise specified.
- Use SQL as the sole data source for services to avoid data drift caused by front-end "direct file reading";
- Cleaning rules and business constraints are set in advance, and prediction and matching results are traceable;
- The management interface supports initialization and user governance, making it suitable for collaborative development environments.
- The UI adopts Chinese business semantics and a layout of dark sidebar + light content area, emphasizing stability, professionalism and readability.
- The prediction/matching input area uses a floating panel, making it easy to remain interactive while scrolling through long pages.
- The homepage charts use a zoned color scheme to avoid difficulties in identification caused by images with the same color.
- The login page supports custom background images and masking enhancements to ensure information readability.
- Adding a light-colored background to the page title area reduces the amount of white space at the top of the page and enhances its visual hierarchy.
- The left navigation bar remains fully visible as the page scrolls, ensuring uninterrupted operation on long pages.
- The salary heatmap's "National Heatmap" and "TOP10 Ranking" containers are highly unified, making the page visually more harmonious.

## 11. Future Development Direction
- Added incremental cleaning tasks and scheduling orchestration;
- Added model drift monitoring and data quality alerts;
- Introduce a stronger semantic model to improve job matching accuracy;
- Provides multi-tenancy and fine-grained permission control.

## 12. Document Reading Guide
- Documents categorized by reader group can be found in: `docs/DOC_INDEX.md`