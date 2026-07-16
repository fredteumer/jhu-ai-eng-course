<?php
// Part 2C/D: salary lookup with a WHERE clause.
//
// !!! INTENTIONALLY VULNERABLE !!!
// User input is concatenated straight into the SQL string (the classic
// w3schools-style pattern). This is the code we ATTACK. It uses
// mysqli_query(), which executes a SINGLE statement -- remember that when
// analysing why stacked-query payloads fail.
include 'db.php';

$empno = isset($_POST['empno']) ? $_POST['empno'] : '';

// Quoted string context, exactly like the w3schools tutorial the PDF links.
$sql = "SELECT emp_no, salary FROM salaries WHERE emp_no = '$empno'";

// Stream the result (unbuffered) so a successful injection that returns the
// whole 2.8M-row table doesn't exhaust PHP memory. We still count every row.
$result = mysqli_query($conn, $sql, MYSQLI_USE_RESULT);

$DISPLAY_CAP = 100;
$rows = [];
$total = 0;
if ($result) {
    while ($row = mysqli_fetch_assoc($result)) {
        $total++;
        if ($total <= $DISPLAY_CAP) { $rows[] = $row; }
    }
    mysqli_free_result($result);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Salary Lookup Result</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; }
    table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
    th, td { border: 1px solid #ccc; padding: .4rem .8rem; text-align: left; }
    th { background: #0b6; color: #fff; }
    .sql { background: #111; color: #6f6; padding: .8rem; border-radius: 4px;
           font-family: monospace; white-space: pre-wrap; word-break: break-all; }
    .err { color: #b00; font-weight: bold; }
    .count { font-weight: bold; }
  </style>
</head>
<body>
  <a href="lookup.html">&larr; back</a>
  <h1>Salary Lookup Result</h1>

  <!-- Echo the executed query so screenshots show exactly what was injected. -->
  <p>Query sent to MySQL:</p>
  <div class="sql"><?php echo htmlspecialchars($sql); ?></div>

<?php
if (!$result) {
    echo '  <p class="err">MySQL error: ' . htmlspecialchars(mysqli_error($conn)) . "</p>\n";
} elseif ($total > 0) {
    echo '  <p class="count">Rows returned: ' . $total;
    if ($total > $DISPLAY_CAP) { echo " (showing first {$DISPLAY_CAP})"; }
    echo "</p>\n";
    echo "  <table>\n    <tr><th>emp_no</th><th>salary</th></tr>\n";
    foreach ($rows as $row) {
        echo "    <tr><td>" . htmlspecialchars($row['emp_no']) . "</td><td>"
           . htmlspecialchars($row['salary']) . "</td></tr>\n";
    }
    echo "  </table>\n";
} else {
    echo "  <p>No matching employee.</p>\n";
}
mysqli_close($conn);
?>
</body>
</html>
