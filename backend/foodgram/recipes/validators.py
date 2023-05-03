from numbers import Number

from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class MinValueValidator(BaseValidator):
    def __init__(self, limit_value: Number, is_included=True) -> None:
        if is_included:
            message = _(
                ('Ensure this value is greater than or equal '
                 'to %(limit_value)s.'))
        else:
            message = _('Ensure this value is greater than %(limit_value)s.')

        self.is_included = is_included

        super().__init__(limit_value, message)

    code = 'tuned_min_value'

    def compare(self, value, limit_value):
        if self.is_included:
            return value < limit_value
        else:
            return value <= limit_value
