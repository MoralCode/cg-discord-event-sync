from dataclasses import dataclass

from sqlalchemy.orm import registry
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

mapper_registry = registry()


@mapper_registry.mapped
@dataclass
class CalendarSubscription:
	__table__ = Table(
        "calendar_subscription",
        mapper_registry.metadata,
        Column("cg_group_id", Integer, primary_key=True),
        Column("discord_server_id", Integer),
    )
	cg_group_id:int
	discord_server_id: int


@mapper_registry.mapped
@dataclass
class CampusGroups:
	__table__ = Table(
        "campus_groups",
        mapper_registry.metadata,
        Column("cg_group_name", String(256)),
        Column("cg_group_id", Integer, primary_key=True),
    )
	cg_group_id:int
	cg_group_name: str
