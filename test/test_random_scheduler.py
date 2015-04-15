import json
import random

from mock import patch

from pybossa.test.helper import sched
from pybossa.test.default import Test, db, with_context
from pybossa.model.task import Task
from pybossa.model.project import Project
from pybossa.model.user import User
from pybossa.model.task_run import TaskRun
from pybossa.model.category import Category
from factories import TaskFactory, ProjectFactory, TaskRunFactory, AnonymousTaskRunFactory, UserFactory
import pybossa


class TestSched(sched.Helper):
    def setUp(self):
        super(TestSched, self).setUp()
        self.endpoints = ['project', 'task', 'taskrun']

    @with_context
    def test_get_random_task(self):
        self._test_get_random_task()

    def _test_get_random_task(self, user=None):
        task = pybossa.sched.get_random_task(project_id=1)
        assert task is not None, task

        tasks = db.session.query(Task).all()
        for t in tasks:
            db.session.delete(t)
        db.session.commit()
        task = pybossa.sched.get_random_task(project_id=1)
        assert task is None, task
