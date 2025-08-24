
-- Table for storing grants
CREATE TABLE IF NOT EXISTS grants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    timeline TEXT,
    applicants TEXT,
    budget TEXT,
    source_url TEXT
);

-- Table for storing projects
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    timeline TEXT,
    budget TEXT,
    directions TEXT,
    source_url TEXT
);

-- Table for storing matches between grants and projects
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grant_id INTEGER,
    project_id INTEGER,
    match_score INTEGER,
    is_urgent BOOLEAN,
    FOREIGN KEY (grant_id) REFERENCES grants (id),
    FOREIGN KEY (project_id) REFERENCES projects (id)
);
