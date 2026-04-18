# PRD: Media Industry Recruitment Data Analytics Platform

## 1. Project Overview

### 1.1 Background

Job seekers with media-related majors often lack a clear, data-driven understanding of the employment market in mainland China. During the job search process, information asymmetry and low decision-making efficiency are common challenges.

This platform leverages pre-collected job posting data from Zhilian Recruitment to provide multi-dimensional data analysis, salary prediction, and intelligent job matching features. It aims to help media professionals efficiently understand market trends and make better-informed career decisions.

### 1.2 Project Objectives

- Provide multi-dimensional insights into job salaries, skill requirements, and education/experience expectations for media-related positions;
- Implement machine-learning-based salary prediction and multi-strategy job matching;
- Lower the barrier to information access through data visualization and improve job-seeking efficiency.

### 1.3 Target Users

The platform primarily targets job seekers with media-related backgrounds, including both fresh graduates and experienced professionals. Its core goal is to reduce information gaps through data analysis.

The core database covers **14 segmented job roles**, categorized into two major professional clusters:

- **Content Production & Operations**
  - Editor  
  - Content Operations  
  - Advertising  
  - Public Relations  
  - Research & Analysis  
  - Product Manager  
  - Government Affairs  

- **Business Growth & Support**
  - Marketing  
  - Promotion & Paid Acquisition  
  - E-commerce Operations  
  - Offline Operations  
  - Business Operations  
  - Sales Recruitment  
  - Human Resources  

---

## 2. Core Features

### 2.1 Recruitment Data Analysis

- **Feature Description**:  
  Supports filtering by job category and region, and presents multi-dimensional distributions of job data.

- **Analysis Dimensions**:
  - **Salary Distribution**: percentile statistics and salary range proportions;
  - **Education & Experience Requirements**: distribution of education levels (Bachelor’s, Master’s, etc.) and experience ranges (1–3 years, 3–5 years, etc.);
  - **Skill Requirements**: high-frequency skill word clouds and skill co-occurrence relationships.

- **Output Format**:  
  ECharts visualizations (bar charts, pie charts, word clouds).

---

### 2.2 Job Detail Analysis

- **Feature Description**:  
  Provides in-depth trend analysis for a specific job role (e.g., “New Media Operations”).

- **Analysis Content**:
  - **Salary Trends**: salary change curves over the past six months;
  - **Skill Demand**: Top 10 most frequent skills and their proportions;
  - **Company Distribution**: breakdown by industry and company size.

- **Output Format**:  
  Trend charts and statistical tables.

---

### 2.3 Regional Salary Map

- **Feature Description**:  
  Visualizes salary levels and job distribution across different regions in China.

- **Visualization Content**:
  - **Heat Map**: average salary by province;
  - **Bubble Chart**: job volume and salary levels by city.

- **Interaction Logic**:  
  Users can click on a region to view a detailed list of local job postings.

---

### 2.4 Cross-Position Comparison

- **Feature Description**:  
  Allows users to select two different combinations of **job category + city** for side-by-side salary comparison.

- **Comparison Dimensions**:
  - **Core Salary**: direct comparison of average monthly salary;
  - **Salary Structure**: comparison of minimum, average, and maximum salary distributions.

- **Output Format**:
  - **Data Cards**: highlight key salary figures;
  - **Visual Charts**: ECharts bar charts displaying salary differences.

---

### 2.5 Salary Prediction

- **Feature Description**:  
  Predicts a potential salary range based on user-provided personal attributes.

- **Input Fields**:
  - Job role
  - Region
  - Education level
  - Work experience
  - Skill set
  - Company size

- **Output Fields**:
  - Predicted salary range (e.g., 15k–20k RMB/month)
  - Model confidence score

- **Implementation Logic**:  
  A pre-trained machine learning model is loaded and executed in real time to generate predictions.

---

### 2.6 Job Matching

- **Feature Description**:  
  Intelligently matches job postings based on user profiles and supports multiple ranking strategies.

- **Input Fields**:
  - Personal skills
  - Preferred region
  - Desired job role
  - Expected salary

- **Matching Dimensions**:
  - **Skill Match**: overlap between user skills and job requirements (Jaccard coefficient);
  - **Location Match**: consistency between preferred and actual job location;
  - **Role Match**: relevance between desired and actual job role;
  - **Salary Match**: whether job salary falls within the expected range.

- **Priority Strategies**:
  - Comprehensive match
  - Skill-priority
  - Location-priority
  - Salary-priority  
  *(Weights of each dimension are dynamically adjusted)*

- **Output**:
  - A ranked list of job postings with detailed information and per-dimension matching scores.

---

## 3. Technology Stack

### 3.1 Front-End

| Technology | Purpose |
|-----------|--------|
| HTML5 | Page structure |
| CSS3 + Bootstrap | Styling and responsive layout |
| JavaScript | Front-end interaction logic |
| ECharts | Data visualization (charts, maps) |
| jQuery | Simplified DOM operations and AJAX requests |

---

### 3.2 Back-End

| Technology | Purpose |
|-----------|--------|
| Python 3.x | Core development language |
| Flask | Web framework for HTTP requests and routing |
| Flask-CORS | Cross-origin request handling |
| Pandas | Data cleaning and statistical analysis |
| NumPy | Numerical computation support |

---

### 3.3 Data Storage

| Technology | Purpose |
|-----------|--------|
| CSV Files | Storage of cleaned job data and analysis results |
| JSON Files | Model configurations and matching strategy weights |
| Joblib Files | Storage of pre-trained salary prediction models |

---

## 4. Data Pipeline

- **Data Collection**:  
  Job posting data is crawled from Boss Zhipin in HTML format.

- **Data Cleaning**:  
  Deduplication, error correction, and format normalization (e.g., salary string parsing, region name standardization).

- **Data Storage**:  
  Cleaned data is stored as CSV files.

- **Data Analysis**:  
  The backend reads CSV files via Pandas for statistical analysis.

- **Model Inference**:  
  Pre-trained models in Joblib format are loaded to handle salary prediction requests.

- **Visualization**:  
  Analysis results are rendered on the front end using ECharts.