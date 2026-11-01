from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestLmsAccess(TransactionCase):
    """Runs against the demo users and data of the module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager = cls.env.ref('lms_institute.user_lms_manager')
        cls.instructor = cls.env.ref('lms_institute.user_lms_instructor_1')
        cls.other_instructor = cls.env.ref('lms_institute.user_lms_instructor_2')
        cls.student = cls.env.ref('lms_institute.user_lms_student_1')
        cls.python = cls.env.ref('lms_institute.course_python')
        cls.math = cls.env.ref('lms_institute.course_math')
        cls.data_science = cls.env.ref('lms_institute.course_data_science')

    def test_student_sees_only_published_courses(self):
        courses = self.env['lms.course'].with_user(self.student).search([])
        self.assertIn(self.python, courses)
        self.assertNotIn(self.math, courses)

    def test_student_sees_only_own_enrollments(self):
        enrollments = self.env['lms.enrollment'].with_user(self.student).search([])
        self.assertTrue(enrollments)
        self.assertEqual(enrollments.student_id, self.student)

    def test_student_cannot_write(self):
        with self.assertRaises(AccessError):
            self.python.with_user(self.student).write({'name': 'Hacked'})
        enrollment = self.env['lms.enrollment'].search([('student_id', '=', self.student.id)], limit=1)
        with self.assertRaises(AccessError):
            enrollment.with_user(self.student).write({'grade': 100})

    def test_student_sees_lessons_of_enrolled_courses_only(self):
        lessons = self.env['lms.lesson'].with_user(self.student).search([])
        self.assertIn(self.env.ref('lms_institute.lesson_py_1'), lessons)
        # enrolled in Business English only as "dropped"
        self.assertNotIn(self.env.ref('lms_institute.lesson_en_1'), lessons)

    def test_instructor_sees_only_own_courses_and_students(self):
        courses = self.env['lms.course'].with_user(self.instructor).search([])
        self.assertIn(self.python, courses)
        self.assertNotIn(self.math, courses)
        enrollments = self.env['lms.enrollment'].with_user(self.instructor).search([])
        self.assertTrue(enrollments)
        self.assertEqual(enrollments.course_id.instructor_id, self.instructor)

    def test_instructor_cannot_edit_other_course(self):
        with self.assertRaises(AccessError):
            self.math.with_user(self.instructor).write({'name': 'Mine now'})

    def test_manager_sees_everything(self):
        self.assertIn(self.math, self.env['lms.course'].with_user(self.manager).search([]))
        total = self.env['lms.enrollment'].search_count([])
        self.assertEqual(self.env['lms.enrollment'].with_user(self.manager).search_count([]), total)

    def test_progress_and_grade_letter(self):
        enrollment = self.env.ref('lms_institute.enrollment_1')
        self.assertEqual(enrollment.progress, 100.0)
        self.assertEqual(enrollment.grade_letter, 'A')
        partial = self.env.ref('lms_institute.enrollment_2')
        self.assertEqual(partial.progress, 50.0)

    def test_enroll_me(self):
        student = self.env.ref('lms_institute.user_lms_student_4')
        self.python.with_user(student).action_enroll_me()
        self.assertTrue(self.env['lms.enrollment'].search([
            ('course_id', '=', self.python.id), ('student_id', '=', student.id)]))
        with self.assertRaises(UserError):  # already enrolled
            self.python.with_user(student).action_enroll_me()

    def test_enroll_me_full_course(self):
        student = self.env.ref('lms_institute.user_lms_student_4')
        with self.assertRaises(UserError):
            self.data_science.with_user(student).action_enroll_me()

    def test_enroll_me_unpublished_course(self):
        with self.assertRaises((UserError, AccessError)):
            self.math.with_user(self.student).action_enroll_me()
