from typing import Any, Optional, Mapping
from reiter.events.meta import Event
from roughrider.workflow import Transition


class WorkflowTransitionEvent(Event):

    def __init__(self, transition: Transition, obj: Any, namespace: Mapping):
        self.transition = transition
        self.obj = obj
        self.namespace = namespace
