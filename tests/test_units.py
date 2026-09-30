"""
Unit tests for core business logic.

Run with:  python tests/test_units.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, timedelta

from app import app as _app
from utils.validators import (clean_skills, has_pdf_extension, is_strong_password,
                              is_valid_cgpa, is_valid_email, is_valid_phone,
                              is_valid_roll_number)


class TestValidators(unittest.TestCase):
    def test_valid_email(self):
        self.assertTrue(is_valid_email("student@college.edu"))
        self.assertTrue(is_valid_email("a.b+c@sub.example.co"))
        self.assertFalse(is_valid_email("plain"))
        self.assertFalse(is_valid_email("a@b"))
        self.assertFalse(is_valid_email(""))

    def test_valid_phone(self):
        self.assertTrue(is_valid_phone("+919876543210"))
        self.assertTrue(is_valid_phone("9876543210"))
        self.assertFalse(is_valid_phone("123"))
        self.assertFalse(is_valid_phone("abcdefghij"))

    def test_strong_password(self):
        self.assertTrue(is_strong_password("Admin@123"))
        self.assertTrue(is_strong_password("Hr#2026xyz"))
        self.assertFalse(is_strong_password("short1A"))
        self.assertFalse(is_strong_password("alllower1@"))
        self.assertFalse(is_strong_password("NoSymbol123"))

    def test_roll_number(self):
        self.assertTrue(is_valid_roll_number("20CS101"))
        self.assertTrue(is_valid_roll_number("CS/2021/011"))
        self.assertFalse(is_valid_roll_number("ab"))

    def test_cgpa(self):
        self.assertTrue(is_valid_cgpa(9.5))
        self.assertTrue(is_valid_cgpa(0.0))
        self.assertTrue(is_valid_cgpa(10.0))
        self.assertFalse(is_valid_cgpa(10.5))
        self.assertFalse(is_valid_cgpa(-1))

    def test_pdf_extension(self):
        self.assertTrue(has_pdf_extension("resume.pdf"))
        self.assertTrue(has_pdf_extension("RESUME.PDF"))
        self.assertFalse(has_pdf_extension("resume.txt"))
        self.assertFalse(has_pdf_extension("noextension"))

    def test_clean_skills(self):
        self.assertEqual(clean_skills("  Python , SQL ,, Java "), "Python, SQL, Java")
        self.assertEqual(clean_skills(""), None)
        self.assertEqual(clean_skills("   "), None)


class TestRecruiterQuickSignupHelpers(unittest.TestCase):
    def test_parse_roles(self):
        from blueprints.auth import parse_roles
        self.assertEqual(parse_roles("Developer, Data Analyst"), ["Developer", "Data Analyst"])
        self.assertEqual(parse_roles("  Developer ,,  "), ["Developer"])
        self.assertEqual(parse_roles("Developer, developer, DEVELOPER"), ["Developer"])
        self.assertEqual(parse_roles(""), [])
        self.assertEqual(parse_roles(None), [])

    def test_split_vacancies(self):
        from blueprints.auth import split_vacancies
        self.assertEqual(split_vacancies(4, 2), [2, 2])
        self.assertEqual(split_vacancies(5, 2), [3, 2])
        self.assertEqual(split_vacancies(3, 3), [1, 1, 1])
        self.assertEqual(split_vacancies(1, 3), [1, 0, 0])
        self.assertEqual(sum(split_vacancies(11, 4)), 11)

    def test_default_recruiter_name(self):
        from blueprints.auth import default_recruiter_name
        self.assertEqual(default_recruiter_name("hr.manager@acme.com"), "Hr Manager")
        self.assertEqual(default_recruiter_name("ravi_kumar@acme.com"), "Ravi Kumar")


class TestModelsAndQueries(unittest.TestCase):
    def setUp(self):
        self.app = _app
        self.app.config["TESTING"] = True
        self.ctx = self.app.app_context()
        self.ctx.push()
        from extensions import db
        from models import Company, Job, Student, User
        self.db = db
        self.db.drop_all()
        self.db.create_all()
        user = User(email="u@test.com", role="student")
        user.set_password("Pass@1234")
        self.db.session.add(user)
        self.db.session.flush()
        student = Student(user_id=user.id, name="Test Student", roll_number="T001",
                          department="CSE", batch="2022-2026", year=4, cgpa=8.0, backlogs=0)
        self.db.session.add(student)
        company = Company(name="Test Company", is_approved=True)
        self.db.session.add(company)
        self.db.session.flush()
        job = Job(company_id=company.id, title="Developer", description="Code",
                  skills="Python", min_cgpa=7.5, max_backlogs=1, vacancies=2,
                  package=6.0, location="Remote", employment_type="Full-time",
                  deadline=date.today() + timedelta(days=30), is_active=True)
        self.db.session.add(job)
        self.db.session.commit()
        self.student = student
        self.job = job
        self.company = company

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
        self.ctx.pop()

    def test_password_hashing(self):
        self.assertTrue(self.student.user.check_password("Pass@1234"))
        self.assertFalse(self.student.user.check_password("wrong"))

    def test_eligibility(self):
        from utils.queries import already_applied, eligible_jobs_query, is_eligible
        self.assertTrue(is_eligible(self.student, self.job))
        self.assertFalse(already_applied(self.student, self.job))
        self.assertIn(self.job, eligible_jobs_query(self.student))

        self.student.cgpa = 7.0
        self.assertFalse(is_eligible(self.student, self.job))
        self.assertNotIn(self.job, eligible_jobs_query(self.student))

    def test_eligible_jobs_excludes_closed(self):
        from utils.queries import eligible_jobs_query
        self.job.is_active = False
        self.assertEqual(eligible_jobs_query(self.student), [])

    def test_app_stats(self):
        from utils.queries import app_stats, company_stats, student_stats
        stats = app_stats()
        self.assertEqual(stats["students"], 1)
        self.assertEqual(stats["companies"], 1)
        self.assertEqual(company_stats(self.company)["jobs"], 1)
        self.assertEqual(student_stats(self.student)["applied"], 0)

    def test_notification_helper(self):
        from utils.notifications import notify
        from models import Notification
        notify(self.student.user_id, "Hi", "Message", "/student")
        self.db.session.commit()
        self.assertEqual(self.student.user.unread_notifications(), 1)
        self.assertEqual(len(self.student.user.recent_notifications(5)), 1)
        self.student.user.notifications.filter_by(is_read=False).update({"is_read": True})
        self.db.session.commit()
        self.assertEqual(self.student.user.unread_notifications(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
