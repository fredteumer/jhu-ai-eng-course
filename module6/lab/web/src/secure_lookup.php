<?php
// The FIX: a prepared statement with a bound parameter. User input is sent
// to MySQL separately from the query text, so it can never change the
// query's structure -- this is what actually stops SQL injection (not the
// MySQLi library by itself).
include 'db.php';

$empno = isset($_POST['empno']) ? $_POST['empno'] : '';

$stmt = mysqli_prepare($conn, "SELECT emp_no, salary FROM salaries WHERE emp_no = ?");
mysqli_stmt_bind_param($stmt, "i", $empno);   // "i" = bind as integer
mysqli_stmt_execute($stmt);
$result = mysqli_stmt_get_result($stmt);
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Salary Lookup Result (secure)</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; }
    table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
    th, td { border: 1px solid #ccc; padding: .4rem .8rem; text-align: left; }
    th { background: #06b; color: #fff; }
    .note { background: #eef; padding: .8rem; border-radius: 4px; }
  </style>
</head>
<body>
  <a href="secure_lookup.html">&larr; back</a>
  <h1>Salary Lookup Result (prepared statement)</h1>
  <p class="note">Input was bound as an integer parameter, so
     <code><?php echo htmlspecialchars($empno); ?></code> is treated as data,
     not SQL.</p>
<?php
if ($result && mysqli_num_rows($result) > 0) {
    echo "  <table>\n    <tr><th>emp_no</th><th>salary</th></tr>\n";
    while ($row = mysqli_fetch_assoc($result)) {
        echo "    <tr><td>" . htmlspecialchars($row['emp_no']) . "</td><td>"
           . htmlspecialchars($row['salary']) . "</td></tr>\n";
    }
    echo "  </table>\n";
} else {
    echo "  <p>No matching employee.</p>\n";
}
?>
</body>
</html>
