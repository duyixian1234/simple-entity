# Simple-entity

![CI](https://github.com/duyixian1234/simple-entity/workflows/CI/badge.svg?branch=master)
Simeple Entity Type for DDD development.

## Install

```bash
pip install -U simple-entity
```

## Use

```python
class Activity(Entity):
    title: str = "activity"
    timeCreate: datetime = None
    timeStart: datetime = None
    timeEnd: datetime = None
    timeEdit: datetime = None

    def update(self, fields: List[str]):
        self.timeEdit = datetime.now()
        return


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
```
