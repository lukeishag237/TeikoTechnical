PRAGMA foreign_keys = ON;

-- Maps project string to project id integer
CREATE TABLE IF NOT EXISTS Projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT UNIQUE NOT NULL
);

-- Maps tratment string to treatment id integer
CREATE TABLE IF NOT EXISTS Treatments ( 
    treatment_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    treatment_name TEXT UNIQUE NOT NULL 
);

-- Maps condition string to condition id integer
CREATE TABLE IF NOT EXISTS Conditions (
    condition_id INTEGER PRIMARY KEY AUTOINCREMENT,
    condition_name TEXT UNIQUE NOT NULL
);


-- Creates table with entry each subject
-- Correlates each subject with their treatment, condition, and project
-- Assumes each patient is only in one project and received only one treatment
CREATE TABLE IF NOT EXISTS Subjects (
    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    treatment_id INTEGER NOT NULL,
    condition_id INTEGER NOT NULL,
    subject_code TEXT NOT NULL,
    age INTEGER,
    sex TEXT CHECK(sex IN ('M','F')),

    UNIQUE(subject_code),

    FOREIGN KEY (project_id) REFERENCES Projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (treatment_id) REFERENCES Treatments(treatment_id) ON DELETE CASCADE,
    FOREIGN KEY (condition_id) REFERENCES Conditions(condition_id) ON DELETE CASCADE
);

-- Creates table with entry for each sample
-- correlates that sample to the subject
CREATE TABLE IF NOT EXISTS Samples (
    sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    sample_code TEXT,
    sample_type TEXT,
    time_from_start INTEGER,
    response INTEGER, -- BOOLEAN: 1/0 = True/False

    b_cell INTEGER,
    cd8_t_cell INTEGER,
    cd4_t_cell INTEGER,
    nk_cell INTEGER,
    monocyte INTEGER,

    UNIQUE(sample_code)

    FOREIGN KEY (subject_id)
        REFERENCES Subjects(subject_id)
        ON DELETE CASCADE
);

-- Indexes - final step to greatly speed up queries 
CREATE INDEX IF NOT EXISTS idx_subject_project
    ON Subjects(project_id);

CREATE INDEX IF NOT EXISTS idx_subject_treatment 
    ON Subjects(treatment_id);

CREATE INDEX IF NOT EXISTS idx_subject_condition
    ON Subjects(condition_id);


CREATE INDEX IF NOT EXISTS idx_samples_subject
    ON Samples(subject_id);

-- implements a raw csv viewer which is used in our dashboard
CREATE VIEW IF NOT EXISTS raw_csv_view AS
SELECT
    Projects.project_name AS project,
    Subjects.subject_code AS subject,
    Conditions.condition_name AS condition,
    Subjects.age,
    Subjects.sex,
    Treatments.treatment_name AS treatment,
    Samples.response,
    Samples.sample_code AS sample,
    Samples.sample_type,
    Samples.time_from_start AS time_from_treatment_start,
    Samples.b_cell,
    Samples.cd8_t_cell,
    Samples.cd4_t_cell,
    Samples.nk_cell,
    Samples.monocyte
FROM Samples
JOIN Subjects ON Samples.subject_id = Subjects.subject_id
JOIN Projects ON Subjects.project_id = Projects.project_id
JOIN Treatments ON Subjects.treatment_id = Treatments.treatment_id
JOIN Conditions ON Subjects.condition_id = Conditions.condition_id;
