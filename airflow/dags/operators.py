from airflow.models import BaseOperator
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from typing import List, Dict, Optional

from utils import APP_ENV, APP_MOUNT


LOCAL = True
DOCKER_URL = "tcp://host.docker.internal:2375"
DOCKER_IMG = "spotify-data-mining_app"
DOCKER_NETWORK = "spotify-data-mining_app-net"
DOCKER_VOL = "spotify-data-mining_app-vol"
DOCKER_VOL_RECOMM = "spotify-data-mining_recomm-vol"

RECOMM_MOUNT = "/recommendation"


class OperatorType:
    def __call__(self, *, task_id: str, cmd: List[str]) -> BaseOperator:
        ...


def operator_factory(img: str, env: Optional[Dict] = None) -> OperatorType:
    if LOCAL:
        return _create_docker_operator(img, env)
    else:
        raise NotImplementedError("Cloud Operator is not implemented yet.")


def _create_docker_operator(img: str, env: Optional[Dict] = None) -> OperatorType:
    env = {} if env is None else env

    def inner(*, task_id: str, cmd: List[str]) -> DockerOperator:
        return DockerOperator(task_id=task_id,
                              docker_url=DOCKER_URL,
                              image=img,
                              command=cmd,
                              environment=env,
                              network_mode=DOCKER_NETWORK,
                              auto_remove=True,
                              mounts=[Mount(target=APP_MOUNT, source=DOCKER_VOL), Mount(target=RECOMM_MOUNT, source=DOCKER_VOL_RECOMM)],
                              mount_tmp_dir=False)

    return inner


Operator = operator_factory(DOCKER_IMG, APP_ENV)
