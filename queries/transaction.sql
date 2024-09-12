CREATE TYPE transaction_type AS ENUM ('credit', 'balance', 'debit', 'refund');

CREATE TABLE transaction (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id UUID NOT NULL REFERENCES wallet(id),
    amount FLOAT NOT NULL,
    type transaction_type NOT NULL,
    description VARCHAR,
    source VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transaction_id ON transaction(id);
CREATE INDEX idx_transaction_wallet_id ON transaction(wallet_id);
