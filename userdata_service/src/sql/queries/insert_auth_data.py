QUERY = '''
INSERT INTO authentification_data
(
    user_id,
    username,
    encoded_password
)
VALUES (
    :user_id,
    :username,
    :encoded_password
)
;
'''
