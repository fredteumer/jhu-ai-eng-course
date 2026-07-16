<?php
// Part 2A: retrieve (emp_no, salary) pairs and display them.
// Modeled on the w3schools "PHP MySQL Select Data" example the assignment links.
//
// The real employees DB has ~2.8M salary rows, so we show a capped page and
// report the true total. Remove the LIMIT to dump the entire table.
include 'db.php';

$total = 0;
if ($r = mysqli_query($conn, "SELECT COUNT(*) AS c FROM salaries")) {
    $total = (int) mysqli_fetch_assoc($r)['c'];
}

$DISPLAY_CAP = 200;
$sql = "SELECT emp_no, salary FROM salaries ORDER BY emp_no LIMIT $DISPLAY_CAP";
$result = mysqli_query($conn, $sql);
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>All Salaries</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 520px; margin: 2rem auto; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: .4rem .8rem; text-align: left; }
    th { background: #0b6; color: #fff; }
    a { display: inline-block; margin-bottom: 1rem; }
  </style>
</head>
<body>
  <a href="index.html">&larr; back</a>
  <h1>Employee Salaries</h1>
  <p>Total rows in <code>salaries</code>: <strong><?php echo number_format($total); ?></strong>
     (showing first <?php echo $DISPLAY_CAP; ?>)</p>
  <table>
    <tr><th>emp_no</th><th>salary</th></tr>
<?php
if ($result && mysqli_num_rows($result) > 0) {
    while ($row = mysqli_fetch_assoc($result)) {
        echo "    <tr><td>" . htmlspecialchars($row['emp_no']) . "</td><td>"
           . htmlspecialchars($row['salary']) . "</td></tr>\n";
    }
} else {
    echo "    <tr><td colspan='2'>No results</td></tr>\n";
}
mysqli_close($conn);
?>
  </table>
</body>
</html>
