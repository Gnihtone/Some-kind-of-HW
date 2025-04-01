
QUERY='''
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE posts_data (
    post_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_private BOOLEAN NOT NULL DEFAULT false,
    tags TEXT[]
);

CREATE TABLE comments_data (
    comment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID NOT NULL REFERENCES posts_data(post_id) ON DELETE CASCADE,
    commentator_user_id UUID NOT NULL,
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reactions_data (
    reaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID NOT NULL REFERENCES posts_data(post_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    reaction_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE idempotency_data (
    idempotency_token VARCHAR(255) PRIMARY KEY,
    payload TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_creator ON posts_data(creator_user_id);
CREATE INDEX idx_comments_post ON comments_data(post_id);
CREATE INDEX idx_reactions_post ON reactions_data(post_id);
'''
