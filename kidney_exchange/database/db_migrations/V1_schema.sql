CREATE TYPE USER_ROLE AS ENUM (
    'viewer',
    'editor',
    'admin'
    );

CREATE TYPE PATIENT_TYPE AS ENUM (
    'recipient',
    'donor',
    'bridging_donor',
    'altruist'
    );

CREATE TYPE COUNTRY AS ENUM (
    'CZE',
    'AUT',
    'IL'
    );

CREATE TYPE BLOOD_TYPE AS ENUM (
    'A',
    'B',
    'AB',
    '0'
    );


CREATE TABLE app_user (
    id        BIGSERIAL NOT NULL PRIMARY KEY,
    email     VARCHAR   NOT NULL UNIQUE, -- serves as username
    pass_hash VARCHAR   NOT NULL,
    role      VARCHAR   NOT NULL
);

CREATE TABLE patient (
    id               BIGSERIAL    NOT NULL PRIMARY KEY,
    id_medical       VARCHAR      NOT NULL,
    country          COUNTRY      NOT NULL,
    patient_type     PATIENT_TYPE NOT NULL,
    blood            BLOOD_TYPE   NOT NULL,
    acceptable_blood VARCHAR      NOT NULL, -- list of BLOOD_TYPE
    typization       VARCHAR      NOT NULL, -- JSON
    luminex          VARCHAR      NOT NULL, -- JSON
    active           BOOLEAN      NOT NULL  -- assume some patients fall out of the set
);

CREATE TABLE patient_pair (
    id           BIGSERIAL NOT NULL PRIMARY KEY,
    recipient_id BIGINT    NOT NULL REFERENCES patient(id) ON DELETE CASCADE ON UPDATE CASCADE,
    donor_id     BIGINT    NOT NULL REFERENCES patient(id) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (recipient_id, donor_id)
);

CREATE TABLE config (
    id         BIGSERIAL NOT NULL PRIMARY KEY,
    parameters VARCHAR   NOT NULL UNIQUE,                 -- structured JSON
    created    TIMESTAMP NOT NULL,
    created_by BIGINT    NOT NULL REFERENCES app_user(id) -- this is also valid for pairing_result
);

CREATE TABLE pairing_result (
    id                   BIGSERIAL NOT NULL PRIMARY KEY,
    config_id            BIGINT    NOT NULL REFERENCES config(id) ON DELETE CASCADE ON UPDATE CASCADE,
    patient_ids          VARCHAR   NOT NULL, -- list of patient_id (or JSON)
    calculated_matchings VARCHAR   NOT NULL, -- JSON
    score_matrix         VARCHAR   NOT NULL, -- matrix (list of lists) of computed compatibility indexes among patients
    created              TIMESTAMP NOT NULL,
    valid                BOOLEAN   NOT NULL
);

-- TODO add indexes (probably only when actually needed)