# Meta Marketing Analytics Flask REST API & Web Dashboard
This project is built on top of the Meta Marketing Ad Insights API and aims to provide a REST API written in Flask Framework and a web-based visual and interactive dashboard that consumes Flask API to make it easier for digital marketing specialists and marketing data analysts to extract data, gain insights, measure and evaluate their digital marketing campaigns.

## Quick Start 

You'll need start two different Flask application which are located at ```dashboard``` and ```insights-api```

1. **Clone the project**
```git clone https://github.com/cetinfikri07/marketing-analytics-flask-api.git```

2. **Create database named meta and load ```meta.sql``` file into your MySQL server**
```bash
mysql -u <username> -p -e "CREATE DATABASE meta " 
mysql -u <username> -p meta < meta.sql
```
