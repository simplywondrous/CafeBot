CREATE TABLE CafeSettings (
    user_id TEXT PRIMARY KEY,
    selected_cafe TEXT NOT NULL
);

CREATE TABLE PriceSettings (
    user_id TEXT PRIMARY KEY,
    price_bool INTEGER NOT NULL
);

CREATE TABLE UserIds (
    user_id TEXT
);