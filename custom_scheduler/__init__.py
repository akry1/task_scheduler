import pybossa.sched as sched
from pybossa.forms.forms import TaskSchedulerForm
from flask.ext.plugins import Plugin
from functools import wraps

__plugin__ = "CustomScheduler"
__version__ = "0.0.1"

SCHEDULER_NAME = 'Custom'


#This method changes according to the priority
def get_task_ids(project_id, user_id=None, user_ip=None):
    """Get tasks based on the creation time for a given project and user."""
    rows = None
    if user_id and not user_ip:
        query = sched.text('''
                     SELECT id FROM task WHERE NOT EXISTS
                     (SELECT task_id FROM task_run WHERE
                     project_id=:project_id AND user_id=:user_id
                        AND task_id=task.id)
                     AND project_id=:project_id AND state !='completed'
                     ORDER BY created DESC, id ASC LIMIT 10''')
        rows = sched.session.execute(query, dict(project_id=project_id,
                                           user_id=user_id))
    else:
        if not user_ip:
            user_ip = '127.0.0.1'
        query = sched.text('''
                     SELECT id FROM task WHERE NOT EXISTS
                     (SELECT task_id FROM task_run WHERE
                     project_id=:project_id AND user_ip=:user_ip
                        AND task_id=task.id)
                     AND project_id=:project_id AND state !='completed'
                     ORDER BY created DESC, id ASC LIMIT 10''')
        rows = sched.session.execute(query, dict(project_id=project_id,
                                           user_ip=user_ip))

    return [t.id for t in rows]


def get_task(project_id, user_id=None, user_ip=None,
                    n_answers=30, offset=0):
    """Return a random task for the user."""
    #project = project_repo.get(project_id)
    candidate_task_ids = get_task_ids(project_id, user_id, user_ip)
    total_remaining = len(candidate_task_ids) - offset
    if total_remaining <= 0:
        return None
    return sched.session.query(sched.Task).get(candidate_task_ids[offset])



def with_custom_scheduler(f):
    @wraps(f)
    def wrapper(project_id, sched, user_id=None, user_ip=None, offset=0):
        if sched == SCHEDULER_NAME:
            return get_task(project_id, user_id, user_ip, offset=offset)
        return f(project_id, sched, user_id=user_id, user_ip=user_ip, offset=offset)
    return wrapper


def variants_with_custom_scheduler(f):
    @wraps(f)
    def wrapper():
        return f() + [(SCHEDULER_NAME, 'Custom')]
    return wrapper


class CustomScheduler(Plugin):

    def setup(self):
        sched.new_task = with_custom_scheduler(sched.new_task)
        sched.sched_variants = variants_with_custom_scheduler(sched.sched_variants)
        TaskSchedulerForm.update_sched_options(sched.sched_variants())
