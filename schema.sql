DROP DATABASE IF EXISTS talent_acquisition;
CREATE DATABASE talent_acquisition;
USE talent_acquisition;

-- Users table (common for both candidates and employees)
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role ENUM('candidate', 'employer') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Companies

CREATE TABLE IF NOT EXISTS companies (
    id VARCHAR(36) PRIMARY KEY,
    employer_id VARCHAR(36) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_email VARCHAR(255) NOT NULL,
    company_phone VARCHAR(20),
    company_website VARCHAR(255),
    company_logo VARCHAR(255),
    est_since VARCHAR(50),
    team_size VARCHAR(50),
    about_company TEXT,
    country VARCHAR(100),
    city VARCHAR(100),
    company_address TEXT,
    embed_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Candidate profiles
CREATE TABLE IF NOT EXISTS candidate_profiles (
    profile_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    resume_path VARCHAR(255),
    headline VARCHAR(255),
    summary TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Education entries for candidates
CREATE TABLE IF NOT EXISTS education (
    education_id VARCHAR(36) PRIMARY KEY,
    candidate_id VARCHAR(36) NOT NULL,
    institution VARCHAR(255) NOT NULL,
    degree VARCHAR(255) NOT NULL,
    field_of_study VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE
);

-- Experience entries for candidates
CREATE TABLE IF NOT EXISTS experience (
    experience_id VARCHAR(36) PRIMARY KEY,
    candidate_id VARCHAR(36) NOT NULL,
    company VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE
);

-- Skills for candidates
CREATE TABLE IF NOT EXISTS skills (
    skill_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Many-to-many relationship between candidates and skills
CREATE TABLE IF NOT EXISTS candidate_skills (
    candidate_id VARCHAR(36) NOT NULL,
    skill_id VARCHAR(36) NOT NULL,
    proficiency ENUM('beginner', 'intermediate', 'advanced', 'expert') NOT NULL,
    PRIMARY KEY (candidate_id, skill_id),
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- Job listings
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(36) PRIMARY KEY,
    company_id VARCHAR(36) NOT NULL,
    employer_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    specialisms TEXT,
    job_type VARCHAR(50) NOT NULL,
    salary VARCHAR(100) NOT NULL,
    career_level VARCHAR(100),
    experience VARCHAR(100),
    gender VARCHAR(50),
    industry VARCHAR(100),
    qualification VARCHAR(255),
    deadline DATE NOT NULL,
    status ENUM('active', 'expired', 'closed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Job applications
CREATE TABLE IF NOT EXISTS applications (
    application_id VARCHAR(36) PRIMARY KEY,
    job_id VARCHAR(36) NOT NULL,
    candidate_id VARCHAR(36) NOT NULL,
    status ENUM('applied', 'under review', 'shortlisted', 'rejected', 'interview scheduled', 'offer extended', 'hired') DEFAULT 'applied',
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    cover_letter TEXT,
    resume_path VARCHAR(255),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES candidate_profiles(profile_id) ON DELETE CASCADE,
    UNIQUE KEY (job_id, candidate_id)
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    notification_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
); 

