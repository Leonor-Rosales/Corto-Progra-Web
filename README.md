# Tarea 7 - API de Tareas y Estudiantes (Flask + Postman)

## Ejecutar
```bash
pip install -r requirements.txt
python app.py          # http://127.0.0.1:5000
```
Cada arranque recrea `tareas.db` con datos de ejemplo (3 estudiantes, 4 tareas).

## Probar en Postman
1. Importar `Tarea7-API.postman_collection.json` (Import > File).
2. Con el servidor corriendo, abrir la colección > **Run** (Collection Runner).
3. Para repetir la corrida completa, reiniciar `python app.py` (restablece los datos).

La variable `baseUrl` (por defecto `http://127.0.0.1:5000`) se puede cambiar en la colección.

## Endpoints
| Acción | Método | Endpoint | Códigos |
| --- | --- | --- | --- |
| Consultar tareas | GET | /api/tareas/ | 200 |
| Consultar una tarea | GET | /api/tareas/{id}/ | 200, 404 |
| Filtrar por estado | GET | /api/tareas/?estado=valor | 200, 400 |
| Completar tarea | PATCH | /api/tareas/{id}/ | 200, 400, 404 |
| Eliminar tarea | DELETE | /api/tareas/{id}/ | 204, 404 |
| Consultar estudiantes | GET | /api/estudiantes/ | 200 |
| Consultar estudiante | GET | /api/estudiantes/{id}/ | 200, 404 |
| Crear estudiante | POST | /api/estudiantes/ | 201, 400, 409 |
| Modificar estudiante | PUT | /api/estudiantes/{id}/ | 200, 400, 404, 409 |
| Eliminar estudiante | DELETE | /api/estudiantes/{id}/ | 204, 404 |

Notas de diseño:
- PATCH en tareas (solo cambia `estado`); PUT en estudiantes (se envía `nombre` y `email`).
- Eliminar un estudiante elimina también sus tareas (`ON DELETE CASCADE`).
- `email` es único: repetirlo devuelve 409.
- Los errores devuelven `{"error": "mensaje"}`.
