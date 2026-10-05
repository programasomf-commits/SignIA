from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String
from backend.app.db.database import Base


class DatasetMuestra(Base):
    __tablename__ = "dataset_master"

    id = Column(Integer, primary_key=True, index=True)
    glosa = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    confianza = Column(Float, nullable=False)
    fecha_captura = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )