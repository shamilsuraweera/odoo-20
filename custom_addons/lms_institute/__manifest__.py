{
    'name': 'Institute LMS',
    'summary': 'Courses, lessons and enrollments for a learning institute',
    'description': """
Learning management for any learning institute.

* Courses with lessons, an instructor, a fee and a seat limit
* Student enrollments with lesson progress and grades
* Three access levels: Student, Instructor and Manager
* Demo users and demo data for every role
""",
    'category': 'Education',
    'version': '1.0',
    'license': 'LGPL-3',
    'author': 'Shamil Suraweera',
    'application': True,
    'depends': ['base', 'mail'],
    'data': [
        'security/lms_security.xml',
        'security/ir.access.csv',
        'views/lms_course_views.xml',
        'views/lms_lesson_views.xml',
        'views/lms_enrollment_views.xml',
        'views/lms_menus.xml',
    ],
    'demo': [
        'data/lms_demo_users.xml',
        'data/lms_demo.xml',
    ],
}
