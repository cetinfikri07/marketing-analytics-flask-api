# Meta Marketing Analytics Flask REST API & Web Dashboard
This project is built on top of the Meta Marketing Ad Insights API and aims to provide a REST API written in Flask Framework and a web-based visual and interactive dashboard that consumes Flask API to make it easier for digital marketing specialists and marketing data analysts to extract data, gain insights, measure and evaluate their digital marketing campaigns.

## Quick Start 

You'll need start two different Flask application which are located at ```dashboard``` and ```insights-api```

1. Clone the project
```git clone https://github.com/cetinfikri07/marketing-analytics-flask-api.git```

2. Create database named meta and load ```meta.sql``` file into your MySQL server
```bash
mysql -u username -p -e "CREATE DATABASE meta " 
mysql -u username -p meta < meta.sql
```
3. Run Flask applications
```bash
python insights-api/main.py
python dashboard/main.py
```
4. Visit http://localhost:5000/ you'll be redirected to the login page automatically, you can login with using example user credentials as
* **Username:** user01@example.com
* **Password:** user

Now you are all set to start using the app. In the demo account there are 2 different ad accounts you can switch accounts from the dropdown menu and see graphs and different metrics that indicates demo account's ad account performance. 

### Main Functionalities

* Flexiblity on different levels as account, campaign, adset, ad.
* Action type option to calculate conversions, cost per action and conversion rates.
* Date range option.
* Time series, distribution by country, age and gender.
* New ad account can be inserted.

If you are wondering how your ad account is performing, you can register your ad account as follows;
* Click profile icon and log out from demo account.
* Create a new account with using your own credentials and log into your account.
* After you logged in you'll see a warning message that says you should register and account.
* Click register and fill out the with your facebook account ID.
* Select date range for the data to be extracted and click register data.

It may take some time to load your data depending on number of days you were requested.
Once the loading process is done go to home page and start to see your insights on each level;

* How many impressions, clicks, conversions you got depending on the specific action type.
* How much moneys is spend on ads.
* Import KPI's such as Cost per Click, Cost per Action, Click through Rate, Conversion Rate.
* Time series of spendings, impressions, clicks etc.
* Country, age and gender distribution on map and bar plot.