from odoo import api, fields, models
from odoo.exceptions import UserError


class LmsCourse(models.Model):
    _name = 'lms.course'
    _description = 'Course'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, copy=False, tracking=True)
    active = fields.Boolean(default=True)
    description = fields.Html()
    state = fields.Selection(
        [('draft', 'Draft'), ('published', 'Published'), ('closed', 'Closed')],
        default='draft', required=True, tracking=True)
    instructor_id = fields.Many2one(
        'res.users', string='Instructor', tracking=True,
        domain=lambda self: [
            ('all_group_ids', 'in', self.env.ref('lms_institute.group_lms_instructor').id)])
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id, required=True)
    fee = fields.Monetary(currency_field='currency_id')
    max_students = fields.Integer(string='Seats', help="Maximum number of students, 0 for no limit.")
    lesson_ids = fields.One2many('lms.lesson', 'course_id', string='Lessons')
    enrollment_ids = fields.One2many('lms.enrollment', 'course_id', string='Enrollments')
    lesson_count = fields.Integer(compute='_compute_lesson_count')
    duration_hours = fields.Float(compute='_compute_duration_hours', store=True)
    enrollment_count = fields.Integer(compute='_compute_enrollment_count')
    is_enrolled = fields.Boolean(compute='_compute_is_enrolled')

    _code_uniq = models.Constraint('unique(code)', 'The course code must be unique.')

    @api.depends('lesson_ids')
    def _compute_lesson_count(self):
        for course in self:
            course.lesson_count = len(course.lesson_ids)

    @api.depends('lesson_ids.duration_minutes')
    def _compute_duration_hours(self):
        for course in self:
            course.duration_hours = sum(course.lesson_ids.mapped('duration_minutes')) / 60

    @api.depends('enrollment_ids.state')
    def _compute_enrollment_count(self):
        for course in self:
            # sudo: seats taken must count every student, not only the ones the user may read
            active = course.sudo().enrollment_ids.filtered(lambda e: e.state != 'dropped')
            course.enrollment_count = len(active)

    def _compute_is_enrolled(self):
        enrolled = self.env['lms.enrollment'].sudo().search([
            ('course_id', 'in', self.ids),
            ('student_id', '=', self.env.uid),
            ('state', '!=', 'dropped'),
        ]).course_id
        for course in self:
            course.is_enrolled = course in enrolled

    def action_publish(self):
        self.state = 'published'

    def action_close(self):
        self.state = 'closed'

    def action_draft(self):
        self.state = 'draft'

    def action_enroll_me(self):
        """Let the current student enroll in a published course."""
        self.ensure_one()
        if self.state != 'published':
            raise UserError(self.env._("You can only enroll in a published course."))
        enrollment = self.env['lms.enrollment'].sudo()
        existing = enrollment.search([
            ('course_id', '=', self.id), ('student_id', '=', self.env.uid)])
        if existing.filtered(lambda e: e.state != 'dropped'):
            raise UserError(self.env._("You are already enrolled in this course."))
        if self.max_students and self.enrollment_count >= self.max_students:
            raise UserError(self.env._("This course is full."))
        if existing:
            existing.state = 'enrolled'
        else:
            enrollment.create({'course_id': self.id, 'student_id': self.env.uid})
        return True
