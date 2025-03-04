QUERY = '''
INSERT INTO tokens_data (
    token,
    user_id,
    created_at,
    active_until
) VALUES (
    :token,
    :user_id,
    :created_at,
    :active_until
);
'''
