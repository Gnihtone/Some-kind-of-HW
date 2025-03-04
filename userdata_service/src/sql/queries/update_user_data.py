QUERY = '''
UPDATE users_data
SET
    name = :name,
    surname = :surname,
    status = :status,
    gender = :gender,
    version = version + 1
WHERE
    user_id = :user_id
;
'''
