CREATE TABLE Department(
dept_id SERIAL,
dept_name VARCHAR(50),
PRIMARY KEY (dept_id)
);

CREATE TABLE Professor(
prof_id SERIAL,
name VARCHAR(20),
salary DOUBLE PRECISION,
dept_id INTEGER NOT NULL,
PRIMARY KEY (prof_id),
FOREIGN KEY (dept_id) references Department(dept_id)
);

CREATE TABLE Course(
course_id SERIAL PRIMARY KEY,
course_name VARCHAR(20),
dept_id INTEGER NOT NULL,
FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
);

CREATE TABLE Student(
student_id SERIAL PRIMARY KEY,
name VARCHAR(20),
gpa Double Precision CHECK (gpa<=4 AND gpa >=0)
);

CREATE TABLE Enrollment(
enrollment_id Serial Primary KEY, 
student_id INTEGER NOT NULL,
course_id INTEGER NOT NULL,
professor_id INTEGER NOT NULL,
grade Double Precision CHECK (grade<=4 AND grade >=0),
FOREIGN KEY (student_id) REFERENCES Student(student_id),
FOREIGN KEY (course_id) REFERENCES Course(course_id),
FOREIGN KEY (professor_id) REFERENCES Professor(prof_id)
);

--Insert into ====================================================================================

INSERT INTO Department (dept_id, dept_name) 
VALUES
(1, 'Biology'),
(2, 'Computer Science'),
(3, 'Mathematics'),
(4, 'Physics');

INSERT INTO Professor(prof_id, name, salary, dept_id) VALUES
(1,'Dr. Smith', '85000.00', 1),
(2,'Dr. Williams', '95000.00', 2),
(3,'Dr. Brown', '88000.00', 3),
(4,'Dr. Johnson', '92000.00', 4);

INSERT INTO Course(course_id, course_name, dept_id) VALUES
(1, 'Advanced Algorithms', 2),
(3, 'Quantum Mechanics', 4),
(2, 'Molecular Biology', 1),
(4, 'Linear Algebra', 3);

INSERT INTO Student(student_id, name, gpa) VALUES
(1, 'Alice', 4),
(2, 'David', 3.6),
(3, 'Bob', 3.5),
(4, 'Charlie',3.8)
;

INSERT INTO Enrollment (student_id, course_id, professor_id, grade) VALUES
(1, 1, 1, 4),
(3, 4, 4, 3.5),
(2, 4, 4, 3.7),
(4, 3, 2, 4),
(2, 2, 3, 3.8);

--=====================================================================================
-- Запит 4 --
SELECT 
    s.name,
    'High Performer' as status
FROM Student s
WHERE s.gpa >= 3.7
UNION ALL
SELECT 
    s.name,
    'Average Performer' as status
FROM Student s
WHERE s.gpa >= 3.5 AND s.gpa < 3.7
UNION ALL
SELECT 
    s.name,
    'Low Performer' as status
FROM Student s
WHERE s.gpa < 3.5;


-- Запит 3 --
SELECT 
    c.course_name,
    p.name as professor,
    d.dept_name,
    COUNT(DISTINCT e.student_id) as enrolled_students,
    ROUND(AVG(e.grade)::numeric, 2) as avg_course_grade,
    MAX(e.grade) as max_grade,
    MIN(e.grade) as min_grade
FROM Course c
LEFT JOIN Enrollment e ON c.course_id = e.course_id
LEFT JOIN Professor p ON e.professor_id = p.prof_id
LEFT JOIN Department d ON c.dept_id = d.dept_id
GROUP BY c.course_name, p.name, d.dept_name
ORDER BY avg_course_grade DESC;

-- Запит 2 --
SELECT DISTINCT 
    s1.name as student1, 
    s2.name as student2,
    e1.grade,
    e1.course_id as course1,
    e2.course_id as course2
FROM Student s1
JOIN Enrollment e1 ON s1.student_id = e1.student_id
JOIN Student s2 ON s1.student_id < s2.student_id
JOIN Enrollment e2 ON s2.student_id = e2.student_id
WHERE e1.grade = e2.grade AND e1.course_id != e2.course_id;

-- Запит 1 --
SELECT 
    d.dept_name,
    COUNT(DISTINCT p.prof_id) as professor_count,
    SUM(p.salary) as total_salary,
    AVG(p.salary) as avg_salary,
    MIN(p.salary) as min_salary,
    MAX(p.salary) as max_salary,
    STDDEV(p.salary) as salary_deviation,
    MODE() WITHIN GROUP (ORDER BY p.salary) as mode_salary
FROM Department d
LEFT JOIN Professor p ON d.dept_id = p.dept_id
GROUP BY d.dept_name;

DROP TABLE Enrollment;
DROP TABLE Course;
DROP TABLE Professor;
DROP TABLE Department;
DROP TABLE Student;
