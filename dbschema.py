from dataclasses import dataclass

from sqlalchemy.orm import registry
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String, ForeignKey

mapper_registry = registry()

Base = mapper_registry.generate_base()

@dataclass
class CalendarSubscription(Base):
	__tablename__ = "calendar_subscription"
	group_id = Column("cg_group_id", Integer, ForeignKey("campus_groups.cg_group_id"))
	server_id = Column("discord_server_id", Integer, primary_key=True)


@dataclass
class CampusGroups(Base):
	__tablename__ = "campus_groups"
	name = Column("cg_group_name", String(256))
	identifier = Column("cg_group_id", Integer, primary_key=True)
