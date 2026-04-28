from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class LeadRecord(Base):
    """Все квалифицированные лиды — постоянное хранилище."""
    __tablename__ = "leads"

    id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    flow = Column(String(1))                  # A или B
    score = Column(String(10))                # hot / warm / cold / off
    contact = Column(String)
    contact_type = Column(String)
    company_name = Column(String)
    city = Column(String)
    object_type = Column(String)
    area_m2 = Column(Float)
    offer_text = Column(Text)
    recommended_action = Column(String)
    raw_text = Column(Text)
    source_url = Column(String)
    bitrix_deal_id = Column(String)           # ID сделки в Bitrix24 после создания
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)


class DuplicateFingerprint(Base):
    """Отпечатки для дедупликации — чтобы не обрабатывать одно и то же дважды."""
    __tablename__ = "duplicates"

    fingerprint = Column(String, primary_key=True)   # hash(contact + source_url)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentLog(Base):
    """Логи работы агентов для аналитики и отладки."""
    __tablename__ = "agent_logs"

    id = Column(String, primary_key=True)
    agent = Column(String)                    # agent2 / agent3 / agent5 / agent6
    action = Column(String)                   # fetched / scored / sent_to_crm / replied
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return Session()
