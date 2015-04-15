import json
import random

from mock import patch

from pybossa.model.task import Task
from pybossa.model.project import Project
from pybossa.model.user import User
from pybossa.model.task_run import TaskRun
from pybossa.model.category import Category
import pybossa

import sys
import os
sys.path.append(os.path.abspath("./pybossa/test"))
from helper import sched
from default import Test, db, with_context
from factories import ProjectFactory, TaskFactory


class TestSched(sched.Helper):

    @with_context
    def test_get_random_task(self, user=None):
        project = ProjectFactory.create()
        TaskFactory.create_batch(3, project=project)
        task = pybossa.sched.new_task(project_id=1, sched='random')

        assert task is not None, task

        tasks = pybossa.core.db.session.query(Task).all()
        for t in tasks:
            pybossa.core.db.session.delete(t)
        pybossa.core.db.session.commit()
        task = pybossa.sched.new_task(project_id=1, sched='random')
        assert task is None, task
