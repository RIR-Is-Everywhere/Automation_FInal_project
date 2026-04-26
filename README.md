# 🚀 QAHarbor Automation Framework

[![Playwright](https://img.shields.io/badge/Playwright-v1.40+-28a745.svg?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Python](https://img.shields.io/badge/Python-3.9+-3776ab.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-Latest-006699.svg?style=flat-square&logo=pytest&logoColor=white)](https://docs.pytest.org/)

A premium, enterprise-grade automated testing suite for the **QA Harbor Job Portal**. This framework implements the **Page Object Model (POM)** pattern, providing robust, scalable, and maintainable end-to-end (E2E) test coverage.

---

## 🌟 Key Features

- **🏆 Comprehensive Coverage**: 55+ test cases covering Authentication, Registration (Candidate & Recruiter), Job Applications, Profile Management, Security, and Accessibility.
- **🏗️ Page Object Model (POM)**: Decoupled test logic from UI elements for maximum stability.
- **🔄 Dynamic Data Generation**: Integrated `utils/helpers.py` for generating unique, realistic test data (Unique Emails, Usernames, Phone Numbers).
- **🛡️ Security & Performance**: Dedicated suites for SQL Injection, XSS prevention, and page load time benchmarks.
- **📸 Automated Visuals**: Auto-screenshot capture on test failure for rapid debugging.
- **📊 Detailed Reporting**: Clean console output with summary tables and optional Allure reporting compatibility.

---

## 📂 Project Architecture

```text
Final_Project/
├── 📄 conftest.py          # Framework configuration & global fixtures
├── 📁 pages/               # Page Object Model Implementations
│   ├── base_page.py        # Core browser actions & abstractions
│   ├── login_page.py       # Authentication flows
│   ├── registration_page.py# Multi-role registration (Candidate/Recruiter)
│   ├── profile_page.py     # User dashboard & account management
│   └── jobs_page.py        # Job search & filtering logic
├── 📁 tests/               # Test Suite Categorization (TC_001 - TC_010)
│   ├── test_TC001_login.py
│   ├── test_TC002_form_submission.py
│   └── ... (All 10 Test Categories)
├── 📁 utils/               # Shared Utilities
│   ├── test_data.py        # Constants & validation payloads
│   └── helpers.py          # Data factories & state managers
└── 📁 screenshots/         # Artifacts from test executions
```

---

## 🛠️ Getting Started

### 1. Prerequisites
- **Python 3.9+**
- **pip** (Python package manager)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/RIR-Is-Everywhere/Automation_FInal_project.git
cd Automation_FInal_project

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

---

## 🚀 Execution Guide

### Run Full Test Suite
```bash
pytest -v
```

### Run Specific Test Scenarios
```bash
# Authentication tests
pytest tests/test_TC001_login.py -v

# Security validation
pytest tests/test_TC003_security.py -v

# Performance benchmarks
pytest tests/test_TC006_performance.py -v
```

---

## 📑 Test Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Default User** | `01625568609` | `secret` |
| **Dummy Users** | *Auto-generated* | *Randomized* |

---

## 📸 Failure Traceability
In the event of a failure, the framework automatically captures the state of the application. Artifacts are stored in the `screenshots/` directory with the prefix `FAIL_`.

---

## 🤝 Contribution
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---
**Developed with ❤️ by Antigravity AI**
