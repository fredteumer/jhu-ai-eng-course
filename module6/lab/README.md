# Module 6 — Disposable SQL Injection Lab 🎓

A throwaway LAMP stack in Docker for the JHU WebSec / SQL Injection assignment.
Everything runs in containers; **nothing is installed on your host.**

## Use

```bash
./setup.sh      # build + start; prints the URL
./teardown.sh   # delete containers, DB volume, and built image
```

Web interface: <http://localhost:8080>

| Page | Purpose | Assignment part |
| --- | --- | --- |
| `module4.php` | list all `(emp_no, salary)` pairs | Part 2A |
| `lookup.html` → `lookup.php` | salary lookup by employee number — **vulnerable** | Part 2B–D |
| `secure_lookup.html` → `secure_lookup.php` | same, prepared statement (the fix) | Part 3 |
| `info.php` | PHP configuration page | Part 1 |

## Stack

- **db**: MySQL 8.4, root password `password`, non-root app user `student`/`student`,
  auto-loaded `employees` database (compact recreation of datacharmer/test_db).
- **web**: PHP 8.3 + Apache with the **MySQLi** extension — the exact
  "PHP 8 + MySQLi" scenario the assignment's Part 3 asks you to analyze.

## Screenshots to capture (maps to the grading rubric)

**Part 1 (20 pts)** — run these on the host while the lab is up:

```bash
docker compose ps                          # both containers "healthy"/"running"
docker compose exec web php -v             # PHP 8 version
docker compose exec db mysql -uroot -ppassword -e "SHOW DATABASES;"
```
…plus browser shots of `http://localhost:8080/` and `http://localhost:8080/info.php`.

> The assignment's rubric literally asks for `systemctl status apache2` / `mysql`.
> The container equivalent is `docker compose ps` (services healthy). If your
> grader expects the `systemctl` output specifically, capture that on the JHU VM
> instead — see the note in the module write-up.

**Part 2 (45 pts)** — three injection attempts in `lookup.html`, screenshot each
result page (it prints the exact query sent to MySQL).

**Part 3 (25 pts)** — compare `lookup.php` vs `secure_lookup.php` behavior.

## Notes

- To make screenshot URLs read `websec.jhu` instead of `localhost`, add
  `127.0.0.1 websec.jhu` to `/etc/hosts` (needs sudo, one line, reversible) and
  browse `http://websec.jhu:8080`. Optional.
- Live-edit any file under `web/src/` — no rebuild needed (it's bind-mounted).
