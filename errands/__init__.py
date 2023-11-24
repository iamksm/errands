import logging

from errands.queues import ProjectErrands

PROJECT_ERRANDS = ProjectErrands()


logging.basicConfig(
    level=logging.INFO,
    format="[ERRANDS] %(levelname)s %(asctime)s %(name)s:%(lineno)s %(message)s",
)
