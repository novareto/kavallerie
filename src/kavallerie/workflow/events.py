from typing import Any, Mapping
from kavallerie.events import Event
from kavallerie.workflow.components import Transition


class WorkflowTransitionEvent(Event):

    def __init__(self, transition: Transition, obj: Any, namespace: Mapping):
        self.transition = transition
        self.obj = obj
        self.namespace = namespace
