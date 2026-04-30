-- Practice 8: PostgreSQL Stored Procedures for PhoneBook
-- Requires helper functions from functions.sql (normalize_phone, is_valid_kz_phone)

-- 1) Upsert procedure: insert or update by username
CREATE OR REPLACE PROCEDURE upsert_contact(p_username VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql
AS $$
DECLARE
    v_phone TEXT := normalize_phone(p_phone);
BEGIN
    IF NOT is_valid_kz_phone(v_phone) THEN
        RAISE EXCEPTION 'Invalid phone format for %: %', p_username, p_phone
            USING ERRCODE = '22023'; -- invalid_parameter_value
    END IF;

    INSERT INTO contacts(username, phone)
    VALUES (p_username, v_phone)
    ON CONFLICT (username) DO UPDATE SET phone = EXCLUDED.phone;
END;
$$;

-- 2) Bulk upsert with validation: accepts arrays; logs invalid rows
--    p_strict=true: skip invalid rows and log to invalid_import_rows
--    p_strict=false: attempt to insert normalized value if passes validation, else skip & log
CREATE OR REPLACE PROCEDURE upsert_many_contacts(
    p_usernames TEXT[],
    p_phones TEXT[],
    p_strict BOOLEAN DEFAULT TRUE
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    u TEXT;
    ph_raw TEXT;
    ph_norm TEXT;
BEGIN
    IF array_length(p_usernames, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Array lengths differ: usernames=% phones=%',
            array_length(p_usernames,1), array_length(p_phones,1)
            USING ERRCODE = '2202E'; -- array_subscript_error
    END IF;

    IF p_usernames IS NULL OR array_length(p_usernames, 1) IS NULL THEN
        RETURN;
    END IF;

    FOR i IN 1..array_length(p_usernames, 1) LOOP
        u := p_usernames[i];
        ph_raw := p_phones[i];
        ph_norm := normalize_phone(ph_raw);

        IF NOT is_valid_kz_phone(ph_norm) THEN
            INSERT INTO invalid_import_rows(username, phone, reason)
            VALUES (u, ph_raw, 'Invalid phone format');
            CONTINUE;
        END IF;

        INSERT INTO contacts(username, phone)
        VALUES (u, ph_norm)
        ON CONFLICT (username) DO UPDATE SET phone = EXCLUDED.phone;
    END LOOP;
END;
$$;

-- 3) Delete procedure: by username or phone (one of them must be provided)
CREATE OR REPLACE PROCEDURE delete_contact(
    p_username VARCHAR DEFAULT NULL,
    p_phone VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted INT;
BEGIN
    IF p_username IS NULL AND p_phone IS NULL THEN
        RAISE EXCEPTION 'Provide p_username or p_phone'
            USING ERRCODE = '22004'; -- null_value_not_allowed
    END IF;

    IF p_username IS NOT NULL THEN
        DELETE FROM contacts WHERE username = p_username;
        GET DIAGNOSTICS v_deleted = ROW_COUNT;
        IF v_deleted > 0 THEN
            RETURN;
        END IF;
    END IF;

    IF p_phone IS NOT NULL THEN
        DELETE FROM contacts WHERE phone = normalize_phone(p_phone);
    END IF;
END;
$$;

