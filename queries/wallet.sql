CREATE TABLE wallet (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    user_phone_number VARCHAR UNIQUE NOT NULL REFERENCES users(phone_number),
    balance FLOAT DEFAULT 0.0,
    is_blocked BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_wallet_id ON wallet(id);
CREATE INDEX idx_wallet_user_phone_number ON wallet(user_phone_number);
