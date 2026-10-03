from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./biblioteca.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    rol = Column(String, default="socio")

    prestamos = relationship("Prestamo", back_populates="usuario")
    reservas = relationship("Reserva", back_populates="usuario")

class Libro(Base):
    __tablename__ = "libros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    ejemplares_totales = Column(Integer, default=1)
    ejemplares_disponibles = Column(Integer, default=1)

    prestamos = relationship("Prestamo", back_populates="libro")
    reservas = relationship("Reserva", back_populates="libro")

class Prestamo(Base):
    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    fecha_prestamo = Column(DateTime, default=datetime.utcnow)
    fecha_dev_estimada = Column(DateTime, nullable=False)
    fecha_dev_real = Column(DateTime, nullable=True)
    estado = Column(String, default="activo")

    usuario = relationship("Usuario", back_populates="prestamos")
    libro = relationship("Libro", back_populates="prestamos")
    multa = relationship("Multa", back_populates="prestamo", uselist=False)

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    fecha_reserva = Column(DateTime, default=datetime.utcnow)
    estado = Column(String, default="pendiente")

    usuario = relationship("Usuario", back_populates="reservas")
    libro = relationship("Libro", back_populates="reservas")

class Multa(Base):
    __tablename__ = "multas"

    id = Column(Integer, primary_key=True, index=True)
    prestamo_id = Column(Integer, ForeignKey("prestamos.id"), nullable=False)
    monto = Column(Float, nullable=False)
    pagada = Column(String, default="pendiente")

    prestamo = relationship("Prestamo", back_populates="multa")