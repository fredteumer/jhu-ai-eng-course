-- Compact, self-contained recreation of the MySQL `employees` sample database.
-- Same tables the real datacharmer/test_db uses (employees, departments,
-- dept_emp, titles, salaries) but with a handful of rows -- plenty to
-- demonstrate SQL injection against the `salaries` table without a 160MB clone.

USE employees;

CREATE TABLE employees (
    emp_no      INT           NOT NULL,
    birth_date  DATE          NOT NULL,
    first_name  VARCHAR(14)   NOT NULL,
    last_name   VARCHAR(16)   NOT NULL,
    gender      ENUM('M','F') NOT NULL,
    hire_date   DATE          NOT NULL,
    PRIMARY KEY (emp_no)
);

CREATE TABLE departments (
    dept_no   CHAR(4)     NOT NULL,
    dept_name VARCHAR(40) NOT NULL,
    PRIMARY KEY (dept_no),
    UNIQUE KEY (dept_name)
);

CREATE TABLE dept_emp (
    emp_no    INT     NOT NULL,
    dept_no   CHAR(4) NOT NULL,
    from_date DATE    NOT NULL,
    to_date   DATE    NOT NULL,
    PRIMARY KEY (emp_no, dept_no)
);

CREATE TABLE titles (
    emp_no    INT         NOT NULL,
    title     VARCHAR(50) NOT NULL,
    from_date DATE        NOT NULL,
    to_date   DATE,
    PRIMARY KEY (emp_no, title, from_date)
);

CREATE TABLE salaries (
    emp_no    INT  NOT NULL,
    salary    INT  NOT NULL,
    from_date DATE NOT NULL,
    to_date   DATE NOT NULL,
    PRIMARY KEY (emp_no, from_date)
);

INSERT INTO departments (dept_no, dept_name) VALUES
    ('d001','Marketing'), ('d002','Finance'), ('d003','Human Resources'),
    ('d004','Production'), ('d005','Development'), ('d006','Quality Management'),
    ('d007','Sales'), ('d008','Research'), ('d009','Customer Service');

INSERT INTO employees (emp_no, birth_date, first_name, last_name, gender, hire_date) VALUES
    (10001,'1953-09-02','Georgi','Facello','M','1986-06-26'),
    (10002,'1964-06-02','Bezalel','Simmel','F','1985-11-21'),
    (10003,'1959-12-03','Parto','Bamford','M','1986-08-28'),
    (10004,'1954-05-01','Chirstian','Koblick','M','1986-12-01'),
    (10005,'1955-01-21','Kyoichi','Maliniak','M','1989-09-12'),
    (10006,'1953-04-20','Anneke','Preusig','F','1989-06-02'),
    (10007,'1957-05-23','Tzvetan','Zielinski','F','1989-02-10'),
    (10008,'1958-02-19','Saniya','Kalloufi','M','1994-09-15'),
    (10009,'1952-04-19','Sumant','Peac','F','1985-02-18'),
    (10010,'1963-06-01','Duangkaew','Piveteau','F','1989-08-24'),
    (10011,'1953-11-07','Mary','Sluis','F','1990-01-22'),
    (10012,'1960-10-04','Patricio','Bridgland','M','1992-12-18');

INSERT INTO titles (emp_no, title, from_date, to_date) VALUES
    (10001,'Senior Engineer','1986-06-26',NULL),
    (10002,'Staff','1996-08-03',NULL),
    (10003,'Senior Engineer','1995-12-03',NULL),
    (10004,'Engineer','1986-12-01','1995-12-01'),
    (10004,'Senior Engineer','1995-12-01',NULL),
    (10005,'Senior Staff','1996-09-12',NULL),
    (10006,'Senior Engineer','1990-08-05',NULL),
    (10007,'Senior Staff','1996-02-11',NULL),
    (10008,'Assistant Engineer','1998-03-11','2000-07-31'),
    (10009,'Assistant Engineer','1985-02-18','1990-02-18'),
    (10010,'Engineer','1996-11-24',NULL),
    (10011,'Staff','1990-01-22','1996-11-09'),
    (10012,'Engineer','2000-12-18',NULL);

INSERT INTO salaries (emp_no, salary, from_date, to_date) VALUES
    (10001,88958,'2002-06-22','9999-01-01'),
    (10002,72527,'2001-08-02','9999-01-01'),
    (10003,43311,'2001-12-01','9999-01-01'),
    (10004,74057,'2001-11-27','9999-01-01'),
    (10005,94692,'2001-09-09','9999-01-01'),
    (10006,43311,'2001-08-02','9999-01-01'),
    (10007,88070,'2002-02-07','9999-01-01'),
    (10008,52668,'2000-07-31','2002-07-31'),
    (10009,94443,'2002-02-14','9999-01-01'),
    (10010,80324,'2001-08-23','9999-01-01'),
    (10011,44935,'1996-11-09','9999-01-01'),
    (10012,63016,'2002-12-16','9999-01-01');

INSERT INTO dept_emp (emp_no, dept_no, from_date, to_date) VALUES
    (10001,'d005','1986-06-26','9999-01-01'),
    (10002,'d007','1996-08-03','9999-01-01'),
    (10003,'d004','1995-12-03','9999-01-01'),
    (10004,'d004','1986-12-01','9999-01-01'),
    (10005,'d003','1989-09-12','9999-01-01'),
    (10006,'d005','1990-08-05','9999-01-01'),
    (10007,'d008','1989-02-10','9999-01-01'),
    (10008,'d005','1998-03-11','2000-07-31'),
    (10009,'d006','1985-02-18','9999-01-01'),
    (10010,'d004','1996-11-24','9999-01-01'),
    (10011,'d009','1990-01-22','9999-01-01'),
    (10012,'d005','2000-12-18','9999-01-01');
