-- Practice 8: PostgreSQL Functions for PhoneBook
-- This file contains functions only. Procedures are in procedures.sql

-- Optional: create schema and base table if they do not exist
CREATE TABLE IF NOT EXISTS contacts (
    username VARCHAR(255) PRIMARY KEY,
    phone VARCHAR(32) NOT NULL
);

-- Table to store invalid rows reported by bulk import procedure
CREATE TABLE IF NOT EXISTS invalid_import_rows (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255),
    phone VARCHAR(32),
    reason TEXT,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Helper: normalize phone (remove spaces, dashes, parentheses)
CREATE OR REPLACE FUNCTION normalize_phone(p_phone TEXT)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_phone TEXT;
BEGIN
    IF p_phone IS NULL THEN
        RETURN NULL;
    END IF;
    v_phone := regexp_replace(p_phone, '[\s\-\(\)]', '', 'g');
    RETURN v_phone;
END;
$$;

-- Helper: validate phone against simple E.164-like rule for KZ numbers
-- Accepts: +77XXXXXXXXX (total length 12), digits only after plus
CREATE OR REPLACE FUNCTION is_valid_kz_phone(p_phone TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v TEXT := normalize_phone(p_phone);
BEGIN
    IF v IS NULL THEN
        RETURN FALSE;
    END IF;
    IF v ~ '^\+77[0-9]{9}$' THEN
        RETURN TRUE;
    END IF;
    RETURN FALSE;
END;
$$;

-- 1) Function: search by pattern across username or phone
CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p_pattern TEXT)
RETURNS TABLE(username VARCHAR, phone VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.username, c.phone
    FROM contacts c
    WHERE c.username ILIKE '%' || COALESCE(p_pattern, '') || '%'
       OR c.phone    ILIKE '%' || COALESCE(p_pattern, '') || '%'
    ORDER BY c.username;
END;
$$;

-- 2) Function: pagination (page by limit/offset)
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(username VARCHAR, phone VARCHAR, total_count BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    -- total_count in each row for convenience (client can read once)
    RETURN QUERY
    WITH total AS (
        SELECT COUNT(*) AS cnt FROM contacts
    )
    SELECT c.username, c.phone, t.cnt
    FROM contacts c
    CROSS JOIN total t
    ORDER BY c.username
    LIMIT GREATEST(p_limit, 0)
    OFFSET GREATEST(p_offset, 0);
END;
$$;

