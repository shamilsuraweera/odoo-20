from odoo import fields, models


class LmsLesson(models.Model):
    _name = 'lms.lesson'
    _description = 'Lesson'
    _order = 'course_id, sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    course_id = fields.Many2one('lms.course', required=True, ondelete='cascade', index=True)
    content = fields.Html()
    duration_minutes = fields.Integer(string='Duration (min)', default=60)
