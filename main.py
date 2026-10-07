from pydantic import BaseModel, ConfigDict, field_validator, PrivateAttr
from dataclasses import dataclass, field
import unittest
from abc import ABC, abstractmethod
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# def check_seconds(value):
#     if type(value) is not int: raise TypeError("Total seconds повинні бути INT")
#     if value < 0: raise ValueError("Total seconds повинні бути > 0")
#
# def _normalize(total_seconds):
#     hours = total_seconds // 3600
#     minutes = (total_seconds % 3600) // 60
#     seconds = (total_seconds % 3600) % 60
#     return hours, minutes, seconds

def adapt_time(total_seconds):
    seconds = total_seconds % 60
    minutes = (total_seconds // 60) % 60
    hours = total_seconds // 3600
    return f"{hours}:{minutes:02d}:{seconds:02d}"

# def check_multiplier(value):
#     if type(value) is not int: raise TypeError("Множник повинен бути INT")
#     if value < 0: raise TypeError("Множник повинен бути > 0")

class TimeValidator(ABC):
    @abstractmethod
    def check_seconds(self, value):
        logger.info("Check total_seconds: %s", value)
        if type(value) is not int: raise TypeError("Total seconds повинні бути INT")
        if value < 0: raise ValueError("Total seconds повинні бути > 0")

    @abstractmethod
    def check_multiplier(self, value):
        logger.info("Перевірка множника: %s", value)
        if type(value) is not int: raise TypeError("Множник повинен бути INT")
        if value < 0: raise TypeError("Множник повинен бути > 0")

class TimeIntervalValidator(TimeValidator):
    def check_seconds(self, value):
        if type(value) is not int: raise TypeError("Total seconds повинні бути INT")
        if value < 0: raise ValueError("Total seconds повинні бути > 0")

    def check_multiplier(self, value):
        if type(value) is not int: raise TypeError("Множник повинен бути INT")
        if value < 0: raise ValueError("Множник повинен бути > 0")

class SimpleTimeIntervalValidator(TimeIntervalValidator): pass
class PydanticTimeIntervalValidator(TimeIntervalValidator): pass
class DataclassTimeIntervalValidator(TimeIntervalValidator): pass

class TimeInterval:
    __slots__ = ("_total_seconds", "_validator")
    def __init__(self, *, total_seconds = 0, validator = None):
        validator = validator or SimpleTimeIntervalValidator()
        validator.check_seconds(total_seconds)

        object.__setattr__(self, "_total_seconds", total_seconds)
        object.__setattr__(self, "_validator", validator)

    @property
    def total_seconds(self):
        return self._total_seconds

    def __setattr__(self, key, value):
        raise AttributeError("Не визначено атрибут")

    def __add__(self, other):
        if type(other) is not TimeInterval: return NotImplemented

        result = self.total_seconds + other.total_seconds
        logger.debug("Додавання: %s + %s = %s", self.total_seconds, other.total_seconds, result)
        logger.debug("Додавання результат: %s", result)
        return TimeInterval(total_seconds=result, validator=self._validator)

    def __sub__(self, other):
        if type(other) is not TimeInterval: return NotImplemented

        result = self.total_seconds - other.total_seconds
        if result < 0: raise ValueError("Результат не може бути < 0")
        logger.debug("Віднімання: %s - %s = %s", self.total_seconds, other.total_seconds, result)
        logger.debug("Віднімання результат: %s", result)
        return TimeInterval(total_seconds=result, validator=self._validator)

    def __mul__(self, multiplier):
        self._validator.check_multiplier(multiplier)
        result = self.total_seconds * multiplier
        logger.debug("Множення: %s * %s = %s", self.total_seconds, multiplier, result)
        logger.debug("Множення результат: %s", result)
        return TimeInterval(total_seconds=result, validator=self._validator)

    def __str__(self):
        return adapt_time(self.total_seconds)

    def __lt__(self, other):
        if type(other) is not TimeInterval: return NotImplemented
        return self.total_seconds < other.total_seconds

class TimeIntervalPydantic(BaseModel):
    total_seconds: int = 0
    model_config = ConfigDict(frozen=True, strict=True)
    _validator: TimeValidator = PrivateAttr()

    def __init__(self, *, total_seconds = 0, validator = None):
        super().__init__(total_seconds=total_seconds)
        self._validator = validator or PydanticTimeIntervalValidator()
        self._validator.check_seconds(total_seconds)

    def __add__(self, other):
        if type(other) is not TimeIntervalPydantic: return NotImplemented

        result = self.total_seconds + other.total_seconds
        logger.debug("[Pydantic]Додавання: %s + %s = %s", self.total_seconds, other.total_seconds, result)
        logger.debug("[Pydantic]Додавання результат: %s", result)
        return TimeIntervalPydantic(total_seconds=result, validator=self._validator)

    def __sub__(self, other):
        if type(other) is not TimeIntervalPydantic: return NotImplemented

        result = self.total_seconds - other.total_seconds
        if result < 0: raise ValueError("Результат не може бути < 0")
        logger.debug("[Pydantic]Віднімання: %s - %s = %s", self.total_seconds, other.total_seconds, result)
        logger.debug("[Pydantic]Віднімання результат: %s", result)
        return TimeIntervalPydantic(total_seconds=result, validator=self._validator)

    def __mul__(self, multiplier):
        self._validator.check_multiplier(multiplier)

        result = self.total_seconds * multiplier
        logger.debug("[Pydantic]Множення: %s * %s = %s", self.total_seconds, multiplier, result)
        logger.debug("[Pydantic]Множення результат: %s", result)
        return TimeIntervalPydantic(total_seconds=result, validator=self._validator)

    def __str__(self):
        return adapt_time(self.total_seconds)

    def __lt__(self, other):
        if type(other) is not TimeIntervalPydantic: return NotImplemented
        return self.total_seconds < other.total_seconds

@dataclass(frozen=True)
class TimeIntervalDataclass:
    total_seconds: int = 0
    validator: TimeValidator = field(default_factory=DataclassTimeIntervalValidator, repr=False, compare=False)

    def __post_init__(self):
        self.validator.check_seconds(self.total_seconds)

    def __add__(self, other):
        if type(other) is not TimeIntervalDataclass: return NotImplemented

        result = self.total_seconds + other.total_seconds
        logger.debug("[Dataclass]Додавання: %s + %s = %s", self.total_seconds, other.total_seconds, result)
        logger.debug("[Dataclass]Додавання результат: %s", result)
        return TimeIntervalDataclass(total_seconds=result, validator=self.validator)

    def __sub__(self, other):
        if type(other) is not TimeIntervalDataclass: return NotImplemented

        result = self.total_seconds - other.total_seconds
        if result < 0: raise ValueError("Результат не може бути < 0")
        logger.debug("[Dataclass]Віднімання: %s - %s = %s", self.total_seconds, other.total_seconds, result)
        logger.debug("[Dataclass]Віднімання результат: %s", result)
        return TimeIntervalDataclass(total_seconds=result, validator=self.validator)

    def __mul__(self, multiplier):
        self.validator.check_multiplier(multiplier)

        result = self.total_seconds * multiplier
        logger.debug("[Dataclass]Множення: %s + %s = %s", self.total_seconds, multiplier, result)
        logger.debug("[Dataclass]Множення результат: %s", result)
        return TimeIntervalDataclass(total_seconds=result, validator=self.validator)

    def __str__(self):
        return adapt_time(self.total_seconds)

    def __lt__(self, other):
        if type(other) is not TimeIntervalDataclass: return NotImplemented
        return self.total_seconds < other.total_seconds

class UnitTests(unittest.TestCase):
    tests = [
        TimeInterval,
        TimeIntervalPydantic,
        TimeIntervalDataclass
    ]

    def test_creation(self):
        for test in self.tests:
            time = test(total_seconds=3661)
            self.assertEqual(time.total_seconds, 3661)

    def test_normalizer(self):
        for test in self.tests:
            time = test(total_seconds=3661)

            self.assertEqual(time.total_seconds, 3661)
            self.assertEqual(str(time), "1:01:01")

    def test_invalid(self):
        invalid_values = [
            "100",
            10.5,
            True,
            None,
            []
        ]

        for test in self.tests:
            for value in invalid_values:
                with self.subTest(tests = test.__name__, value=value):
                    with self.assertRaises((ValueError,TypeError)): test(value)

    def test_negative_value(self):
        for test in self.tests:
            with self.subTest(tests = test.__name__):
                with self.assertRaises(ValueError): test(total_seconds=-1)

    def test_add(self):
        for test in self.tests:
            f1 = test(total_seconds=3600)
            s2 = test(total_seconds=1800)

            result = f1 + s2
            self.assertEqual(result.total_seconds, 5400)
            self.assertEqual(str(result), "1:30:00")

    def test_sub(self):
        for test in self.tests:
            f1 = test(total_seconds=3600)
            s2 = test(total_seconds=1800)

            result = f1 - s2
            self.assertEqual(result.total_seconds, 1800)
            self.assertEqual(str(result), "0:30:00")

    def test_neg_sub(self):
        for test in self.tests:
            f1 = test(total_seconds=1800)
            s2 = test(total_seconds=3600)

            with self.assertRaises(ValueError): f1 - s2

    def test_mul(self):
        for test in self.tests:
            time = test(total_seconds=1800)
            result = time * 3
            self.assertEqual(result.total_seconds, 5400)
            self.assertEqual(str(result), "1:30:00")
            f1 = test(total_seconds=3600)
            s2 = test(total_seconds=1800)

    def test_collections(self):
        for test in self.tests:
            f1 = test(total_seconds=100)
            s2 = test(total_seconds=200)
            s3 = test(total_seconds=300)

            values = [f1, s2, s3]
            values.sort()
            self.assertEqual([x.total_seconds for x in values],[100, 200, 300])
            unique_values = {f1, s2, s3}
            self.assertEqual(len(unique_values), 3)

    def test_di(self):
        validator = SimpleTimeIntervalValidator()
        time = TimeIntervalDataclass(total_seconds=3661, validator=validator)
        self.assertEqual(time.total_seconds, 3661)

    def test_di_replace(self):
        validator = PydanticTimeIntervalValidator()
        time = TimeIntervalDataclass(total_seconds=3661, validator=validator)
        self.assertEqual(time.total_seconds, 3661)
if __name__ == "__main__":
    unittest.main()
