# Installation Guide

## 1. System Requirements

| Requirement  | Minimum                          |
|--------------|----------------------------------|
| Operating System | Windows 10/11, macOS, Linux  |
| Python       | 3.8 or later                    |
| Disk Space   | ~50 MB (app + SQLite + vendor assets) |
| Browser      | Chrome, Edge, Firefox (recent versions) |

No external database server, virtual environment, Docker, or internet connection is required **after** setup — all vendor assets (Bootstrap, Font Awesome, Chart.js) are bundled locally.

## 2. Download Python

If Python is not already installed:

1. Visit https://www.python.org/downloads/
2. Download the latest Python 3.x installer for your OS.
3. **Windows**: run the installer and tick **"Add Python to PATH"** before installing.
4. Verify the installation:

```bash
python --version
```

## 3. Download / Extract the Project

Extract the `PlacementPortal` folder to a convenient location, for example:

```
C:\Users\G Vineeth\PlacementPortal
```

## 4. Install Dependencies

Open a terminal (Command Prompt / PowerShell) and navigate to the project folder:

```bash
cd C:\Users\G Vineeth\PlacementPortal
pip install -r requirements.txt
```

The `requirements.txt` file contains:

| Package            | Version   | Purpose                        |
|--------------------|-----------|--------------------------------|
| Flask              | 3.0.3     | Web framework                  |
| Flask-SQLAlchemy   | 3.1.1     | ORM and database integration   |
| Flask-Login        | 0.6.3     | Session-based authentication   |

## 5. Run the Application

```bash
python app.py
```

Expected output:

```
[SEED] Default admin created -> admin@placement.edu / Admin@123
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

Open your browser and go to **http://127.0.0.1:5000**

The SQLite database (`database.db`) and the `uploads/` folder are created **automatically** on first run. Nothing else needs to be configured.

## 6. Default Login Credentials

| Role      | Email                | Password   |
|-----------|----------------------|------------|
| Admin     | `admin@placement.edu` | `Admin@123` |

Student and recruiter accounts are created by self-registration on the public pages.

## 7. Troubleshooting

| Problem                        | Solution |
|--------------------------------|----------|
| `python` not recognised        | Reinstall Python and tick **"Add to PATH"**, then restart the terminal. |
| `pip install` fails / timeout  | Retry, or run `pip install --user -r requirements.txt`. |
| Port 5000 already in use       | `netstat -ano | findstr :5000`, then kill the process, or edit the port in `app.py` (`app.run(port=5000)`). |
| Blank page / database errors   | Delete `database.db` and `uploads/` and restart — they regenerate automatically. |
| `InsecureRequestWarning`/slow first request | Expected on first startup while hashing the admin password. |

## 8. Resetting the Application

To start with a clean slate, delete the auto-generated `database.db` and `uploads/` folders and run `python app.py` again.

## 9. Running the Tests

Two test suites are included:

```bash
python tests\smoke_test.py    # end-to-end route + flow tests (deletes/recreates database.db)
python tests\test_units.py    # unit tests for validators, models, queries, notifications
```
