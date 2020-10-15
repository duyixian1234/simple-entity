import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Callable, Set, _GenericAlias  # type:ignore

from dateutil.parser import parse

gen_uuid = lambda: str(uuid.uuid4())
logger = logging.getLogger(__name__)
config = dict(gen_uuid=gen_uuid, log=logger.info)


class Config:
    class UniqueIDGenerator:
        def __call__(self):
            return Config.gen_uuid()

    gen_uuid = gen_uuid
    log: Callable = logger.info
    unique_id_generator = UniqueIDGenerator()


class DataclassMeta(type):
    def __new__(cls, *args, **kwargs):
        return dataclass(super().__new__(cls, *args, **kwargs))


class ValueObject(metaclass=DataclassMeta):
    __no_log_methods__ = set(["from_dict", "to_dict"])

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**__get_obj_dict__(data, cls)) if data else None  # type:ignore

    def to_dict(self):
        return asdict(self)

    def __getattribute__(self, key: str):
        value = super().__getattribute__(key)
        if callable(value) and not key.startswith("__") and not key in self.__no_log_methods__:
            return method_call_log(self, key)(value)
        return value


class Entity(ValueObject):
    _id: str = field(default_factory=Config.unique_id_generator)


def __get_obj_dict__(data: dict, _type: type):
    data = __prepare_data__(data, _type)

    obj_dict = {}
    annotations = __get_annotations__(_type)

    for key, value in data.items():
        if isinstance(annotations[key], _GenericAlias):
            if issubclass(annotations[key].__args__[0], ValueObject):
                obj_dict[key] = [annotations[key].__args__[0].from_dict(item) for item in value]
            else:
                obj_dict[key] = value
        elif issubclass(annotations[key], ValueObject):
            obj_dict[key] = annotations[key].from_dict(value)
        else:
            obj_dict[key] = value

    return obj_dict


def __prepare_data__(data: dict, _type: type):
    data = data.copy()
    annotations = __get_annotations__(_type)
    unused = []
    for key, value in data.items():
        if key not in annotations:
            unused.append(key)
            continue
        if annotations[key] == int and not isinstance(value, int):
            data[key] = int(value)
        if annotations[key] == datetime and not isinstance(value, datetime):
            data[key] = value and parse(value)
    for key in unused:
        data.pop(key)
    return data


def __get_annotations__(_type: type):
    annotations = {}
    for parent in _type.mro()[::-1]:
        if hasattr(parent, "__annotations__"):
            annotations.update(parent.__annotations__)
    return annotations


def method_call_log(obj, method_name: str):
    def outter(func):
        def inner(*args, **kwargs):
            Config.log(f'Call method <{method_name}> of {repr(obj)} with args {args} kwargs {kwargs}')
            ret = func(*args, **kwargs)
            return ret

        return inner

    return outter


def basicConfig(*, unique_id_generator: Callable = None, log_func: Callable = None):
    if unique_id_generator:
        Config.gen_uuid = unique_id_generator
    if log_func:
        Config.log = log_func
