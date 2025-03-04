QUERY = '''
SELECT
    user_id,
    username,
    encoded_password
FROM
    authentification_data
WHERE
    username = :username
;
'''
