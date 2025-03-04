QUERY = '''
SELECT
    token
FROM
    tokens_data
WHERE
    token = :token
    AND
    user_id = :user_id
    AND
    active_until > NOW()
;
'''
