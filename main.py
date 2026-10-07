from pydantic import BaseModel, ConfigDict, field_validator
from dataclasses import dataclass
import unittest

def check_seconds(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("Total seconds повинні бути INT")

    if value < 0: raise ValueError("Total seconds повинні бути > 0")

def _normalize(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = (total_seconds % 3600) % 60
    return hours, minutes, seconds

def adapt_time(total_seconds):
    seconds = total_seconds % 60
    minutes = (total_seconds // 60) % 60
    hours = total_seconds // 3600
    return f"{hours}:{minutes:02d}:{seconds:02d}"

def check_multiplier(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("Множник повинен бути INT")

    if value < 0: raise TypeError("Множник повинен бути > 0")

class TimeInterval:
    __slots__ = '_total_seconds'
    def __init__(self, *, total_seconds = 0):
        check_seconds(total_seconds)
        object.__setattr__(self, "_total_seconds", total_seconds)

    @property
    def total_seconds(self):
        return self._total_seconds

    def __setattr__(self, key, value):
        raise AttributeError("Не визначено атрибут")

    def __add__(self, other):
        if not isinstance(other, TimeInterval): return NotImplemented

        result = self.total_seconds + other.total_seconds
        return TimeInterval(total_seconds=result)

    def __sub__(self, other):
        if not isinstance(other, TimeInterval): return NotImplemented

        result = self.total_seconds - other.total_seconds
        if result < 0: raise ValueError("Результат не може бути < 0")
        return TimeInterval(total_seconds=result)

    def __mul__(self, multiplier):
        check_multiplier(multiplier)
        result = self.total_seconds * multiplier
        return TimeInterval(total_seconds=result)

    def __str__(self):
        return adapt_time(self.total_seconds)

    def __lt__(self, other):
        if not isinstance(other, TimeInterval): return NotImplemented
        return self.total_seconds < other.total_seconds

class TimeIntervalPydantic(BaseModel):
    total_seconds: int = 0
    model_config = ConfigDict(frozen=True, strict=True)
    @field_validator('total_seconds')
    @classmethod
    def validate_seconds(cls, value):
        check_seconds(value)
        return value

    def __add__(self, other):
        if not isinstance(other, TimeIntervalPydantic): return NotImplemented

        result = self.total_seconds + other.total_seconds
        return TimeIntervalPydantic(total_seconds=result)

    def __sub__(self, other):
        if not isinstance(other, TimeIntervalPydantic): return NotImplemented

        result = self.total_seconds - other.total_seconds
        if result < 0: raise ValueError("Результат не може бути < 0")
        return TimeIntervalPydantic(total_seconds=result)

    def __mul__(self, multiplier):
        check_multiplier(multiplier)

        result = self.total_seconds * multiplier
        return TimeIntervalPydantic(total_seconds=result)

    def __str__(self):
        return adapt_time(self.total_seconds)

    def __lt__(self, other):
        if not isinstance(other, TimeIntervalPydantic): return NotImplemented
        return self.total_seconds < other.total_seconds

@dataclass(frozen=True)
class TimeIntervalDataclass:
    total_seconds: int = 0

    def __post_init__(self):
        check_seconds(self.total_seconds)

    def __add__(self, other):
        if not isinstance(other, TimeIntervalDataclass): return NotImplemented

        result = self.total_seconds + other.total_seconds
        return TimeIntervalDataclass(total_seconds=result)

    def __sub__(self, other):
        if not isinstance(other, TimeIntervalDataclass): return NotImplemented

        result = self.total_seconds - other.total_seconds
        if result < 0: raise ValueError("Результат не може бути < 0")
        return TimeIntervalDataclass(total_seconds=result)

    def __mul__(self, multiplier):
        check_multiplier(multiplier)

        result = self.total_seconds * multiplier
        return TimeIntervalDataclass(total_seconds=result)

    def __str__(self):
        return adapt_time(self.total_seconds)

    def __lt__(self, other):
        if not isinstance(other, TimeIntervalDataclass): return NotImplemented
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
if __name__ == "__main__":
    unittest.main()
