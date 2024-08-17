from typing import TypedDict


class BuildApiJsonResponse(TypedDict):
    _class: str
    actions: list
    artifacts: list
    building: bool
    description: str | None
    displayName: str
    duration: int
    estimatedDuration: int
    executor: str | None
    fullDisplayName: str
    id: str
    inProgress: bool
    keepLog: bool
    number: int
    queueId: int
    result: str
    timestamp: int
    url: str
    builtOn: str
    changeSet: dict
    culprits: list
