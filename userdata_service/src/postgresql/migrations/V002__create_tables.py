QUERY='''
CREATE TYPE gender AS ENUM ('undefined', 'male', 'female');

CREATE TABLE authentification_data (
    user_id            UUID NOT NULL           PRIMARY KEY,
    username           TEXT NOT NULL,
    encoded_password   TEXT NOT NULL,
    email              TEXT,
    phone_number       TEXT,

    version            INT NOT NULL            DEFAULT 1
);

CREATE TABLE tokens_data (
    token         TEXT NOT NULL              PRIMARY KEY,
    user_id       UUID NOT NULL              REFERENCES authentification_data(user_id),

    created_at    TIMESTAMPTZ NOT NULL       DEFAULT NOW(),
    active_until  TIMESTAMPTZ NOT NULL
);

CREATE TABLE users_data (
    user_id            UUID NOT NULL           REFERENCES authentification_data(user_id),
    name               TEXT NOT NULL,
    surname            TEXT NOT NULL           DEFAULT '',
    status             TEXT NOT NULL           DEFAULT '',
    gender             gender NOT NULL         DEFAULT 'undefined',

    version            INT NOT NULL            DEFAULT 1
);
'''