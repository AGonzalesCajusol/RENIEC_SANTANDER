from fastapi import APIRouter

router = APIRouter(prefix="/reniec", tags=["RENIEC"])


@router.get("/dni/{dni}")
def consultar_dni(dni: str):
    """Consulta de datos de una persona por número de DNI."""
    return {
        "dni": dni,
        "nombres": "Ejemplo Nombres",
        "apellidoPaterno": "Ejemplo Paterno",
        "apellidoMaterno": "Ejemplo Materno",
    }
