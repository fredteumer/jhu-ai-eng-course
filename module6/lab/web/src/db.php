<?php
// Shared connection. Connects as the NON-root 'student' user over the
// private compose network (host "db" = the MySQL container).
$conn = mysqli_connect('db', 'student', 'student', 'employees');
if (!$conn) {
    die('Connection failed: ' . mysqli_connect_error());
}
?>
