-- Create a NON-root application user, as the assignment recommends
-- ("Creating a non-root account ... reflects how a normal user operates").
-- The web app connects as this user, not as root.
CREATE USER IF NOT EXISTS 'student'@'%' IDENTIFIED BY 'student';
GRANT ALL PRIVILEGES ON employees.* TO 'student'@'%';
FLUSH PRIVILEGES;
