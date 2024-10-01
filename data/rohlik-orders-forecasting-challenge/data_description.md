## Dataset Description
You are provided with historical orders data for selected Rohlik warehouses.
The task is to forecast the "orders" column for the test set. Some features
are not available in test as they are not known at the moment of making the
prediction (e.g. precipitation, shutdown, user activity on website). These are
market in the description below.


## Files
* **train.csv** \- the training set containing the historical orders data and selected features described below
* **test.csv** \- the test set
* **solution_example.csv** \- a sample submission file in the correct format
* **train_calendar.csv** \- a calendar for the training set containing data about holidays or warehouse specific events, some columns are already in the train data but there are additional rows in this file for dates where some warehouses could be closed due to public holiday or Sunday (and therefore they are not in the train set)
* **test_calendar.csv** \- a calendar for the test set


## Columns
**train.csv**
* `warehouse` \- warehouse name
* `date` \- date
* `orders` \- number of customer orders attributed to the warehouse
* `holiday_name` \- name of public holiday if any
* `holiday` \- 0/1 indicating the presence of holidays
* `shutdown` \- warehouse shutdown or limitation due to operations **(not provided in test)**
* `mini_shutdown` \- warehouse shutdown or limitation due to operations **(not provided in test)**
* `shops_closed` \- public holiday with most of the shops or large part of shops closed
* `winter_school_holidays` \- school holidays
* `school_holidays` \- school holidays
* `blackout` \- warehouse shutdown or limitation due to operations **(not provided in test)**
* `mov_change` \- a change in minimum order value indicating potential change in customer behaviour **(not provided in test)**
* `frankfurt_shutdown` \- warehouse shutdown or limitation due to operations **(not provided in test)**
* `precipitation` \- precipitation in mm around the location of the warehouse which correlates with location of the customers **(not provided in test)**
* `snow` \- snowfall in mm around the location of the warehouse which correlates with location of the customers **(not provided in test)**
* `user_activity_1` \- user activity on the website **(not provided in test)**
* `user_activity_2` \- user activity on the website **(not provided in test)**
* `id` \- row id consisting of warehouse name and date
**train_calendar.csv**
Contains a subset of the train.csv columns but more rows as it contains all
dates whereas train.csv does not contain dates where warehouse was closed due
to public holidays or other events


## Files
5 files


## Size
1.44 MB


## Type
csv


## License
Subject to Competition Rules


## Data Explorer
1.44 MB
solution_example.csv
test.csv
test_calendar.csv
train.csv
train_calendar.csv


## Summary
5 files
50 columns
