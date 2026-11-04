from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LmsEnrollment(models.Model):
    _name = 'lms.enrollment'
    _description = 'Enrollment'
    _inherit = ['mail.thread']
    _order = 'enrollment_date desc, id desc'

    course_id = fields.Many2one('lms.course', required=True, ondelete='cascade', index=True, tracking=True)
    student_id = fields.Many2one(
        'res.users', string='Student', required=True, index=True, tracking=True,
        domain=lambda self: [
            ('all_group_ids', 'in', self.env.ref('lms_institute.group_lms_student').id)])
    enrollment_date = fields.Date(default=fields.Date.context_today)
    state = fields.Selection(
        [('enrolled', 'Enrolled'), ('completed', 'Completed'), ('dropped', 'Dropped')],
        default='enrolled', required=True, tracking=True)
    completed_lesson_ids = fields.Many2many(
        'lms.lesson', string='Completed Lessons',
        domain="[('course_id', '=', course_id)]")
    progress = fields.Float(compute='_compute_progress', store=True, help="Share of lessons completed, in percent.")
    grade = fields.Float(string='Grade (%)', tracking=True)
    grade_letter = fields.Selection(
        [('A', 'A'), ('B', 'B'), ('C', 'C'), ('S', 'S'), ('F', 'F')],
        compute='_compute_grade_letter', store=True)

    _student_course_uniq = models.Constraint(
        'unique(course_id, student_id)', 'This student is already enrolled in the course.')

    @api.depends('completed_lesson_ids', 'course_id.lesson_ids')
    def _compute_progress(self):
        for enrollment in self:
            total = len(enrollment.course_id.lesson_ids)
            done = len(enrollment.completed_lesson_ids & enrollment.course_id.lesson_ids)
            enrollment.progress = 100.0 * done / total if total else 0.0

    @api.depends('grade', 'state')
    def _compute_grade_letter(self):
        for enrollment in self:
            if enrollment.state != 'completed':
                enrollment.grade_letter = False
            elif enrollment.grade >= 75:
                enrollment.grade_letter = 'A'
            elif enrollment.grade >= 65:
                enrollment.grade_letter = 'B'
            elif enrollment.grade >= 50:
                enrollment.grade_letter = 'C'
            elif enrollment.grade >= 35:
                enrollment.grade_letter = 'S'
            else:
                enrollment.grade_letter = 'F'

    @api.constrains('grade')
    def _check_grade(self):
        if any(not 0 <= enrollment.grade <= 100 for enrollment in self):
            raise ValidationError(self.env._("The grade must be between 0 and 100."))

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_drop(self):
        self.write({'state': 'dropped'})

    def action_reenroll(self):
        self.write({'state': 'enrolled'})
