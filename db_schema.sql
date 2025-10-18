PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS candidates (
  id TEXT PRIMARY KEY,
  full_name TEXT,
  email TEXT,            -- single
  phone TEXT,            -- single
  location TEXT,
  summary TEXT,
  source_file TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id TEXT NOT NULL,
  type TEXT,             -- linkedin|github|portfolio|other
  url TEXT NOT NULL,
  FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS education (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id TEXT NOT NULL,
  institution TEXT NOT NULL,
  degree TEXT,
  field TEXT,
  start_year INTEGER,
  end_year INTEGER,
  FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experience (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id TEXT NOT NULL,
  company TEXT NOT NULL,
  title TEXT,
  start TEXT,      -- 'YYYY' or 'YYYY-MM'
  end TEXT,        -- 'YYYY' | 'YYYY-MM' | NULL
  description TEXT,
  FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id TEXT NOT NULL,
  skill TEXT NOT NULL,
  FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS certifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id TEXT NOT NULL,
  name TEXT NOT NULL,
  year INTEGER,
  issuer TEXT,
  FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

-- Plain (non-expression) indexes
CREATE INDEX IF NOT EXISTS idx_skills_skill ON skills(skill);
CREATE INDEX IF NOT EXISTS idx_edu_institution ON education(institution);
CREATE INDEX IF NOT EXISTS idx_exp_company ON experience(company);
CREATE INDEX IF NOT EXISTS idx_exp_title ON experience(title);
CREATE INDEX IF NOT EXISTS idx_cert_name ON certifications(name);

-- ✅ Expression-based UNIQUE constraints implemented as UNIQUE INDEXES
CREATE UNIQUE INDEX IF NOT EXISTS ux_links ON links(candidate_id, url);

CREATE UNIQUE INDEX IF NOT EXISTS ux_skills ON skills(candidate_id, skill);

CREATE UNIQUE INDEX IF NOT EXISTS ux_education_dedupe
ON education(
  candidate_id,
  institution,
  IFNULL(degree, ''),
  IFNULL(field, ''),
  IFNULL(start_year, -1),
  IFNULL(end_year, -1)
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_experience_dedupe
ON experience(
  candidate_id,
  company,
  IFNULL(title, ''),
  IFNULL(start, ''),
  IFNULL(end, '')
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_certifications_dedupe
ON certifications(
  candidate_id,
  name,
  IFNULL(year, -1),
  IFNULL(issuer, '')
);
