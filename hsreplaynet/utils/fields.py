import shortuuid
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import CharField, PositiveSmallIntegerField, SmallIntegerField
from django.utils.deconstruct import deconstructible


@deconstructible
class IntEnumValidator:
	def __init__(self, enum):
		self.enum = enum

	def __call__(self, value):
		if value not in self.enum._value2member_map_:
			raise ValidationError("%r is not a valid %s" % (value, self.enum.name))

	def __eq__(self, other):
		return isinstance(other, IntEnumValidator) and self.enum == other.enum


class IntEnumField(SmallIntegerField):
	def __init__(self, *args, **kwargs):
		if "enum" in kwargs:
			# if check required for migrations (apparently)
			self.enum = kwargs.pop("enum")
			kwargs["choices"] = tuple((m.value, m.name) for m in self.enum)
			kwargs["validators"] = [IntEnumValidator(self.enum)]
			if "default" in kwargs:
				kwargs["default"] = int(kwargs["default"])
		super(IntEnumField, self).__init__(*args, **kwargs)

	def from_db_value(self, value, expression, connection, context):
		if value is not None:
			try:
				return self.enum(value)
			except ValueError:
				return value
		return value


class PlayerIDField(PositiveSmallIntegerField):
	def __init__(self, *args, **kwargs):
		kwargs["choices"] = ((1, 1), (2, 2))
		kwargs["validators"] = [MinValueValidator(1), MaxValueValidator(2)]
		super(PlayerIDField, self).__init__(*args, **kwargs)


def _shortuuid():
	return shortuuid.uuid()


class ShortUUIDField(CharField):
	def __init__(self, *args, **kwargs):
		kwargs.setdefault("max_length", 22)
		kwargs.setdefault("editable", False)
		kwargs.setdefault("blank", True)
		kwargs.setdefault("unique", True)
		kwargs.setdefault("default", _shortuuid)
		super(ShortUUIDField, self).__init__(*args, **kwargs)