import pytest
from prejudice import ConstraintError, Or
from kavallerie.workflow.components import Action, Transition, Transitions
from kavallerie.workflow import WorkflowContext, WorkflowState, Workflow


class Document:
    state = None
    body = ""


def NonEmptyDocument(item, **namespace):
    if not item.body:
        raise ConstraintError(message='Body is empty.')


class RoleValidator:

    def __init__(self, role):
        self.role = role

    def __call__(self, item, role=None, **namespace):
        if role != self.role:
            raise ConstraintError(
                message=f'Unauthorized. Missing the `{role}` role.')


class PublicationWorkflow(Workflow):

    class states(WorkflowState):
        draft = 'Draft'
        published = 'Published'
        submitted = 'Submitted'

    transitions = Transitions((
        Transition(
            origin=states.draft,
            target=states.published,
            action=Action(
                'Publish',
                constraints=[NonEmptyDocument, RoleValidator('publisher')]
            )
        ),
        Transition(
            origin=states.published,
            target=states.draft,
            action=Action(
                'Retract',
                constraints=[
                    Or((RoleValidator('owner'),
                        RoleValidator('publisher')))
                ]
            )
        ),
        Transition(
            origin=states.draft,
            target=states.submitted,
            action=Action(
                'Submit',
                constraints=[NonEmptyDocument, RoleValidator('owner')],
            )
        ),
        Transition(
            origin=states.submitted,
            target=states.published,
            action=Action(
                'Publish',
                constraints=[NonEmptyDocument, RoleValidator('publisher')],
            )
        )
    ))


def test_workflow_initial_state():
    workflow = PublicationWorkflow(PublicationWorkflow.states.draft)
    assert workflow.default_state is PublicationWorkflow.states.draft
    workflow = PublicationWorkflow('draft')
    assert workflow.default_state is PublicationWorkflow.states.draft

    with pytest.raises(TypeError):
        PublicationWorkflow(12)


def test_publish_worflow():
    workflow = PublicationWorkflow('draft')

    item = Document()
    workflow_item = workflow(item, role='some role')
    assert workflow_item.state == workflow.get('draft')
    assert not workflow_item.get_possible_transitions()

    item.body = "Some text here"
    assert not workflow_item.get_possible_transitions()

    workflow_item = workflow(item, role='owner')
    assert workflow_item.get_possible_transitions() == (
        workflow.transitions[2],
    )

    workflow_item.transition_to(PublicationWorkflow.states.submitted)
    assert workflow_item.state == workflow.get('submitted')
