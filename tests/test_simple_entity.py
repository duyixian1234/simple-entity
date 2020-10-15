from dataclasses import field
from datetime import datetime
from typing import List
from unittest import mock

from simple_entity import Entity, basicConfig


class Activity(Entity):
    title: str = "activity"
    timeCreate: datetime = None
    timeStart: datetime = None
    timeEnd: datetime = None
    timeEdit: datetime = None

    def update(self, fields: List[str]):
        self.timeEdit = datetime.now()
        return


class User(Entity):
    uid: int = 0


class LimitActivity(Activity):
    user: User = None
    amount: int = 0
    left: int = 0


class Users(Entity):
    users: List[User] = field(default_factory=list)
    ids: List[int] = field(default_factory=list)


def test_entity():
    # test base
    activity = Activity(
        _id="0",
        title="act0",
        timeCreate=datetime(2020, 1, 1),
        timeStart=datetime(2020, 1, 1),
        timeEnd=datetime(2020, 1, 10),
    )
    act_dict = {
        "_id": "0",
        "timeCreate": datetime(2020, 1, 1, 0, 0),
        "timeStart": datetime(2020, 1, 1, 0, 0),
        "timeEdit": None,
        "timeEnd": datetime(2020, 1, 10, 0, 0),
        "title": "act0",
    }
    assert activity.to_dict() == act_dict
    assert Activity.from_dict(act_dict) == activity

    # test method logger
    log_func = mock.Mock()
    basicConfig(log_func=log_func)
    activity.update([])
    expect_log = "Call method <update> of Activity(_id='0', title='act0', timeCreate=datetime.datetime(2020, 1, 1, 0, 0), timeStart=datetime.datetime(2020, 1, 1, 0, 0), timeEnd=datetime.datetime(2020, 1, 10, 0, 0), timeEdit=None) with args ([],) kwargs {}"
    log_func.assert_called_once_with(expect_log)

    user = User("u1234", 1234)

    # test inherit
    limit_act_dict = dict(
        title="limit_act",
        timeCreate=datetime(2020, 1, 1),
        timeStart=datetime(2020, 1, 1),
        timeEnd=datetime(2020, 1, 10),
        amount="100",
        left="100",
        user=dict(_id="u1234", uid=1234),
    )

    limit_act = LimitActivity.from_dict(limit_act_dict)
    assert limit_act._id
    assert limit_act.user == user

    # test extra fields
    assert User.from_dict({**user.to_dict(), "extra": ""}) == user

    # test custom unique_id_generator
    basicConfig(unique_id_generator=lambda: "xxxx")
    assert User()._id == "xxxx"

    # test _GenericAlias fields
    assert Users.from_dict(dict(users=[user.to_dict()] * 3, ids=[1, 2, 3])) == Users(
        _id="xxxx", users=[user, user, user], ids=[1, 2, 3]
    )
