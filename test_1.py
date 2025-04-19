import json

a= """
{ "person_age": "int64", "person_income": "double", "person_home_ownership": "String", "person_emp_length": "double", "loan_intent": "String", "loan_grade": "String", "loan_amnt": "double", "loan_int_rate": "double", "loan_status": "int64", "loan_percent_income": "double", "cb_person_default_on_file": "String", "cb_person_cred_hist_length": "int64" }
"""
b=json.loads(a)
print(b)