-- One md5 hash over every row of every seeded table.
-- Same hash = byte-for-byte identical data.
SELECT md5(
    (SELECT string_agg(t::text, '|' ORDER BY t::text) FROM companies t) ||
    (SELECT string_agg(t::text, '|' ORDER BY t::text) FROM users t) ||
    (SELECT string_agg(t::text, '|' ORDER BY t::text) FROM jobs t) ||
    (SELECT string_agg(t::text, '|' ORDER BY t::text) FROM educations t)
);
