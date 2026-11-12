CREATE TABLE companies(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE users(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE jobs(
    user_id INTEGER NOT NULL REFERENCES users (id),
    company_id INTEGER NOT NULL REFERENCES companies (id),
    start_year INTEGER NOT NULL,
    end_year INTEGER,
    CHECK (end_year IS NULL OR end_year > start_year)
);

CREATE TABLE educations(
    user_id INTEGER NOT NULL REFERENCES users (id),
    college_name TEXT NOT NULL
);
