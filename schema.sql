-- Go Slides - SQL Schema for SQLite
-- Run this only if not using Flask-SQLAlchemy create_all()

-- Users (admin/staff)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(128) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event years (only one active)
CREATE TABLE IF NOT EXISTS years (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(64) NOT NULL,
    theme VARCHAR(255),
    active BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activities (competition / non-competition)
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    date DATE,
    type VARCHAR(32) NOT NULL DEFAULT 'competition',
    status VARCHAR(32) NOT NULL DEFAULT 'upcoming',
    quota INTEGER,
    guideline_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (year_id) REFERENCES years(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_activities_year ON activities(year_id);
CREATE INDEX IF NOT EXISTS idx_activities_status ON activities(status);

-- Registrants (Phase 3: check_in_code for QR attendance, attended_at)
CREATE TABLE IF NOT EXISTS registrants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    school VARCHAR(255) NOT NULL,
    phone VARCHAR(64),
    email VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    check_in_code VARCHAR(64) UNIQUE,
    attended_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_registrants_activity ON registrants(activity_id);
CREATE INDEX IF NOT EXISTS idx_registrants_status ON registrants(status);
CREATE INDEX IF NOT EXISTS idx_registrants_check_in_code ON registrants(check_in_code);

-- Gallery (per year/activity, optional featured)
CREATE TABLE IF NOT EXISTS gallery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year_id INTEGER NOT NULL,
    activity_id INTEGER,
    file VARCHAR(255) NOT NULL,
    caption VARCHAR(512),
    is_featured BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (year_id) REFERENCES years(id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_gallery_activity ON gallery(activity_id);
CREATE INDEX IF NOT EXISTS idx_gallery_featured ON gallery(is_featured);

-- About (single row, editable by admin)
CREATE TABLE IF NOT EXISTS about (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL DEFAULT 'About Go Slides',
    description TEXT,
    goals TEXT,
    location VARCHAR(512)
);

-- Contact form submissions
CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activity log (Phase 3: admin action audit)
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(64) NOT NULL,
    entity_type VARCHAR(64),
    entity_id VARCHAR(64),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at);

-- Sponsors table
CREATE TABLE IF NOT EXISTS sponsors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(128) NOT NULL,
    logo VARCHAR(255) NOT NULL,
    link VARCHAR(255),
    year_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (year_id) REFERENCES years(id) ON DELETE CASCADE
);
