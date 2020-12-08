# Matching Algorithm for mealshuttle
### Quickbooks Desktop
to run the task:
- run migrations
- run command `manage.py populate_db` it uses random data, you may want to flush the DB and retry multiple times 
to see different results 
- go to `/admin/matching_algo/company/` you will find the matching restaurants
 listing them according to the criteria in `models.Company.matching_restaurants`
 sorted by the `exposure`