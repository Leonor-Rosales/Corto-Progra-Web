# Tarea 7 - API de Tareas y Estudiantes (Flask + Postman)

## Ejecutar
```bash
pip install -r requirements.txt
python app.py          # http://127.0.0.1:5000
```

## Endpoints
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

