from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import models

app = FastAPI(
    title="Sistema de Gestión de Biblioteca API",
    description="API RESTful para administrar libros, préstamos, reservas, multas y usuarios.",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure DB tables exist on startup
models.Base.metadata.create_all(bind=models.engine)

def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

TARIFA_MULTA_DIARIA = 2000.0

@app.get("/", include_in_schema=False)
def servir_index():
    return FileResponse("index.html")

# -------------------------------------------------------------------
# 1. Autenticación y Usuarios
# -------------------------------------------------------------------
@app.get("/usuarios", tags=["Usuarios"])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()

@app.post("/usuarios", tags=["Usuarios"])
def crear_usuario(nombre: str, email: str, rol: str = "socio", db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")
    
    nuevo_usuario = models.Usuario(
        nombre=nombre,
        email=email,
        hashed_password="123",
        rol=rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

# -------------------------------------------------------------------
# 2. Catálogo de Libros
# -------------------------------------------------------------------
@app.get("/libros/buscar", tags=["Catálogo"])
def buscar_libros(q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Libro)
    if q:
        query = query.filter(
            (models.Libro.titulo.ilike(f"%{q}%")) | 
            (models.Libro.autor.ilike(f"%{q}%")) |
            (models.Libro.categoria.ilike(f"%{q}%"))
        )
    return query.all()

@app.post("/libros", tags=["Catálogo"])
def crear_libro(titulo: str, autor: str, categoria: str, ejemplares: int = 1, db: Session = Depends(get_db)):
    nuevo_libro = models.Libro(
        titulo=titulo, 
        autor=autor, 
        categoria=categoria, 
        ejemplares_totales=ejemplares,
        ejemplares_disponibles=ejemplares
    )
    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)
    return nuevo_libro

# -------------------------------------------------------------------
# 3. Préstamos y Devoluciones
# -------------------------------------------------------------------
@app.post("/prestamos", tags=["Préstamos"])
def registrar_prestamo(usuario_id: int, libro_id: int, dias_prestamo: int = 7, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    libro = db.query(models.Libro).filter(models.Libro.id == libro_id).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    if libro.ejemplares_disponibles < 1:
        raise HTTPException(status_code=400, detail="El libro no está disponible para préstamo. Puedes reservarlo.")

    libro.ejemplares_disponibles -= 1
    fecha_dev = datetime.utcnow() + timedelta(days=dias_prestamo)
    
    nuevo_prestamo = models.Prestamo(
        usuario_id=usuario_id,
        libro_id=libro_id,
        fecha_dev_estimada=fecha_dev
    )
    db.add(nuevo_prestamo)
    db.commit()
    db.refresh(nuevo_prestamo)
    return nuevo_prestamo

@app.post("/prestamos/{prestamo_id}/devolucion", tags=["Préstamos"])
def registrar_devolucion(prestamo_id: int, db: Session = Depends(get_db)):
    prestamo = db.query(models.Prestamo).filter(models.Prestamo.id == prestamo_id).first()
    if not prestamo or prestamo.estado == "devuelto":
        raise HTTPException(status_code=400, detail="Préstamo no válido o ya devuelto.")

    fecha_actual = datetime.utcnow()
    prestamo.fecha_dev_real = fecha_actual
    prestamo.estado = "devuelto"

    libro = db.query(models.Libro).filter(models.Libro.id == prestamo.libro_id).first()
    if libro:
        libro.ejemplares_disponibles += 1

    monto_multa = 0.0
    if fecha_actual > prestamo.fecha_dev_estimada:
        dias_atraso = (fecha_actual - prestamo.fecha_dev_estimada).days
        monto_multa = max(1, dias_atraso) * TARIFA_MULTA_DIARIA
        
        nueva_multa = models.Multa(prestamo_id=prestamo.id, monto=monto_multa)
        db.add(nueva_multa)

    db.commit()

    if monto_multa > 0:
        return {"mensaje": "Libro devuelto con atraso.", "multa_generada": monto_multa}
    return {"mensaje": "Libro devuelto a tiempo sin penalizaciones."}

# -------------------------------------------------------------------
# 4. Reservas de Libros
# -------------------------------------------------------------------
@app.post("/reservas", tags=["Reservas"])
def crear_reserva(usuario_id: int, libro_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    libro = db.query(models.Libro).filter(models.Libro.id == libro_id).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado.")

    if libro.ejemplares_disponibles > 0:
        raise HTTPException(status_code=400, detail="El libro tiene ejemplares disponibles, no es necesario reservarlo.")

    nueva_reserva = models.Reserva(usuario_id=usuario_id, libro_id=libro_id)
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    return nueva_reserva

@app.get("/reservas", tags=["Reservas"])
def listar_reservas(db: Session = Depends(get_db)):
    return db.query(models.Reserva).all()

# -------------------------------------------------------------------
# 5. Reportes y Multas
# -------------------------------------------------------------------
@app.get("/reportes/prestamos-activos", tags=["Reportes"])
def reportes_prestamos_activos(db: Session = Depends(get_db)):
    return db.query(models.Prestamo).filter(models.Prestamo.estado == "activo").all()

@app.get("/multas", tags=["Multas"])
def listar_multas(db: Session = Depends(get_db)):
    return db.query(models.Multa).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)