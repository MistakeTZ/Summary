from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Base model
Base = declarative_base()


# Users model
class User(Base):
    __tablename__ = "users"

    id = Column(  # noqa VNE003
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    telegram_id = Column(Integer, nullable=False, unique=True)
    name = Column(String, nullable=False)
    username = Column(String)
    get_license = Column(Boolean, default=False)
    role = Column(String, nullable=False, default="user")
    restricted = Column(Boolean, nullable=False, default=False)
    registered = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(  # noqa VNE003
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(String, nullable=False)
    link = Column(String, nullable=True)
    description = Column(String, nullable=False)
    order = Column(Integer, default=0)

    photos = relationship("ProjectPhoto", back_populates="project")
    tools = relationship("ProjectTool", back_populates="project")


class ProjectPhoto(Base):
    __tablename__ = "project_photos"

    id = Column(  # noqa VNE003
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    photo_id = Column(String, nullable=False)
    project_id = Column(ForeignKey("projects.id"), nullable=False)

    project = relationship("Project", back_populates="photos")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(  # noqa VNE003
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(String, nullable=False)
    link = Column(String, nullable=True)


class ProjectTool(Base):
    __tablename__ = "project_tools"

    id = Column(  # noqa VNE003
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    tool_id = Column(ForeignKey("tools.id"), nullable=False)
    project_id = Column(ForeignKey("projects.id"), nullable=False)

    project = relationship("Project", back_populates="tools")
    tool = relationship("Tool")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False)
    product = Column(String(255), nullable=True)
    payment_amount = Column(Integer, nullable=True)
    provider_payment_charge_id = Column(String(100), nullable=True)
    telegram_payment_charge_id = Column(String(100), nullable=True)
    registered = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(  # noqa VNE003
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(String, nullable=False)
    token = Column(String, nullable=False)


# Repetitions model
class Repetition(Base):
    __tablename__ = "repetitions"

    id = Column(  # noqa VNE003
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    chat_id = Column(Integer, nullable=False)
    message_id = Column(Integer, nullable=False)
    button_text = Column(String, nullable=False, default="")
    button_link = Column(String, nullable=False, default="")
    time_to_send = Column(DateTime, nullable=True, default=None)
    confirmed = Column(Boolean, nullable=False, default=False)
    is_send = Column(Boolean, nullable=False, default=False)


# Init DB
def init_db(db_path="database/db.sqlite3"):
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
