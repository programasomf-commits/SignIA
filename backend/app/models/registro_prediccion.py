from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String

from backend.app.db.database import Base


class RegistroPrediccion(Base):
    __tablename__ = "registro_predicciones"

    id = Column(Integer, primary_key=True, index=True)
    glosa_predicha = Column(String, nullable=False)
    confianza = Column(Float, nullable=False)
    fecha = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
