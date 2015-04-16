import json
import random
import sys
import os

import pybossa

sys.path.append(os.path.abspath("./pybossa/test"))
from helper import sched as sched_helper
from default import Test, db, with_context
from factories import ProjectFactory, TaskFactory


class TestSched(sched_helper.Helper):

    @with_context
    def test_get_random_task(self, user=None):
        task = pybossa.sched.new_task(project_id=1, sched='random')
        assert task is None, task

        project = ProjectFactory.create()
        TaskFactory.create_batch(3, project=project)
        task = pybossa.sched.new_task(project_id=1, sched='random')

        assert task is not None, task
        assert task.project_id == project.id
