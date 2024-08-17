from typing import TypedDict


class JobApiJsonResponse(TypedDict):
    _class: str
    actions: list
    description: str
    displayName: str
    displayNameOrNull: str
    fullDisplayName: str
    fullName: str
    name: str
    url: str
    buildable: bool
    builds: list
    color: str
    firsBuild: dict
    healthReport: list
    inQueue: bool
    keepDependencies: bool
    lasBuild: dict
    lastCompletedBuild: dict
    lasFailedBuild: dict
    lastStableBuild: dict
    lastSuccessfulBuild: dict
    nextBuildNumber: int
    property: list
    queueItem: None
    concurrentBuild: bool
    disabled: bool
    downstreamProjects: list
    labelExpression: None
    scm: dict
    upstreamProjects: list
