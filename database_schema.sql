-- Database schema for Placement Training System
-- Creates database and all required tables with keys and constraints

CREATE DATABASE IF NOT EXISTS placement_training_system CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
USE placement_training_system;

SET SESSION FOREIGN_KEY_CHECKS=0;

-- Companies
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    eligibility_criteria TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Skills
CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    priority INT DEFAULT 0,
    is_required TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY ux_skills_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Mapping companies to skills
CREATE TABLE IF NOT EXISTS company_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    skill_id INT NOT NULL,
    priority INT DEFAULT 0,
    required TINYINT(1) DEFAULT 1,
    UNIQUE KEY ux_company_skill (company_id, skill_id),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Admins
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(120) NOT NULL UNIQUE,
    email VARCHAR(150) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Students
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    department VARCHAR(120),
    year INT,
    cgpa DECIMAL(3,2) DEFAULT 0.00,
    backlog_count INT DEFAULT 0,
    backlogs INT DEFAULT 0,
    phone VARCHAR(30),
    college_name VARCHAR(255),
    is_active TINYINT(1) DEFAULT 1,
    dream_company_id INT DEFAULT NULL,
    resume_completed TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dream_company_id) REFERENCES companies(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Student selected companies (history/selection)
CREATE TABLE IF NOT EXISTS student_companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    company_id INT NOT NULL,
    selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'selected',
    UNIQUE KEY ux_student_company (student_id, company_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Student skills (proficiency, completion)
CREATE TABLE IF NOT EXISTS student_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    skill_id INT NOT NULL,
    completed TINYINT(1) DEFAULT 0,
    score DECIMAL(5,2) DEFAULT 0.00,
    proficiency INT DEFAULT 0,
    completion_percent INT DEFAULT 0,
    last_practiced_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    UNIQUE KEY ux_student_skill (student_id, skill_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    short_description VARCHAR(512),
    description TEXT,
    problem_statement TEXT,
    difficulty ENUM('Beginner','Intermediate','Advanced') DEFAULT 'Beginner',
    max_score INT DEFAULT 100,
    time_limit_seconds INT DEFAULT 0,
    company_relevance TEXT,
    objectives TEXT,
    requirements TEXT,
    expected_input TEXT,
    expected_output TEXT,
    evaluation_criteria TEXT,
    reference_solution TEXT,
    reference_approach TEXT,
    status ENUM('active','inactive') DEFAULT 'active',
    created_by INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES admins(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Map projects to companies
CREATE TABLE IF NOT EXISTS project_companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    company_id INT NOT NULL,
    UNIQUE KEY ux_project_company (project_id, company_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Map projects to skills
CREATE TABLE IF NOT EXISTS project_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    skill_id INT NOT NULL,
    importance INT DEFAULT 0,
    UNIQUE KEY ux_project_skill (project_id, skill_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Project test cases
CREATE TABLE IF NOT EXISTS project_test_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    input TEXT,
    expected_output TEXT,
    points INT DEFAULT 0,
    is_hidden TINYINT(1) DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Project hints
CREATE TABLE IF NOT EXISTS project_hints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    hint_order INT DEFAULT 1,
    hint TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Project submissions (one per attempt or per upload)
CREATE TABLE IF NOT EXISTS project_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    project_id INT NOT NULL,
    submission_type ENUM('code','zip','github','link') DEFAULT 'code',
    submission_link TEXT,
    file_path VARCHAR(512),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending','evaluating','completed') DEFAULT 'pending',
    score DECIMAL(5,2) DEFAULT 0.00,
    feedback TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Attempts (history of evaluations)
CREATE TABLE IF NOT EXISTS project_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    attempt_number INT DEFAULT 1,
    score DECIMAL(5,2) DEFAULT 0.00,
    passed TINYINT(1) DEFAULT 0,
    failed_test_cases TEXT,
    hints_viewed INT DEFAULT 0,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES project_submissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Learning plans
CREATE TABLE IF NOT EXISTS learning_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    skill_id INT,
    duration_days INT DEFAULT 30,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tasks (daily tasks)
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT,
    day_number INT,
    title VARCHAR(255),
    description TEXT,
    is_optional TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES learning_plans(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Student task progress
CREATE TABLE IF NOT EXISTS student_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    task_id INT NOT NULL,
    completed TINYINT(1) DEFAULT 0,
    status ENUM('not-started','in-progress','completed') DEFAULT 'not-started',
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE KEY ux_student_task (student_id, task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Progress summary per student
CREATE TABLE IF NOT EXISTS progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    project_completion_percent DECIMAL(5,2) DEFAULT 0.00,
    project_performance_percent DECIMAL(5,2) DEFAULT 0.00,
    skill_completion_percent DECIMAL(5,2) DEFAULT 0.00,
    task_completion_percent DECIMAL(5,2) DEFAULT 0.00,
    challenge_performance_percent DECIMAL(5,2) DEFAULT 0.00,
    overall_progress_percent DECIMAL(5,2) DEFAULT 0.00,
    skill_completion DECIMAL(5,2) DEFAULT 0.00,
    task_completion DECIMAL(5,2) DEFAULT 0.00,
    test_performance DECIMAL(5,2) DEFAULT 0.00,
    aptitude_performance DECIMAL(5,2) DEFAULT 0.00,
    discussion_performance DECIMAL(5,2) DEFAULT 0.00,
    overall_progress DECIMAL(5,2) DEFAULT 0.00,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY ux_progress_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Mock interviews
CREATE TABLE IF NOT EXISTS mock_interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    category VARCHAR(100),
    question TEXT,
    student_answer TEXT,
    score DECIMAL(5,2) DEFAULT 0.00,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Resumes
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    content TEXT,
    pdf_path VARCHAR(512),
    completed TINYINT(1) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Certificates
CREATE TABLE IF NOT EXISTS certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    name VARCHAR(255),
    issuer VARCHAR(255),
    issue_date DATE,
    link VARCHAR(512),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Weekly challenges
CREATE TABLE IF NOT EXISTS weekly_challenges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    weight_percent DECIMAL(5,2) DEFAULT 5.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Challenge results
CREATE TABLE IF NOT EXISTS challenge_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_id INT NOT NULL,
    student_id INT NOT NULL,
    score DECIMAL(5,2) DEFAULT 0.00,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (challenge_id) REFERENCES weekly_challenges(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY ux_challenge_student (challenge_id, student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET SESSION FOREIGN_KEY_CHECKS=1;

-- Sample indexes for performance
CREATE INDEX idx_projects_difficulty ON projects(difficulty);
CREATE INDEX idx_students_cgpa ON students(cgpa);

-- End of schema
