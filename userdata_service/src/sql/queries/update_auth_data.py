QUERY = '''
UPDATE authentification_data
SET
    email = :email,
    phone_number = :phone_number,
    version = version + 1
WHERE
    user_id = :user_id
;
'''
