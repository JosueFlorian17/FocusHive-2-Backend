# Definiendo stack tecnológico - backend
## NestJS + Prisma + MySQL

# 🧩 MAPEAMIENTO DE ENDPOINTS POR MÓDULO

## 🔐 Auth Module
Autenticación de usuarios con JWT.

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | Registrar nuevo usuario |
| `POST` | `/auth/login` | Iniciar sesión (devuelve JWT) |
| `GET` | `/auth/profile` | Obtener perfil (token requerido) |
| `POST` | `/auth/logout` | Cerrar sesión (invalida token) |

## 👤 Users Module
Gestión de datos personales y preferencias.

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/users/:id` | Obtener info de usuario |
| `PATCH` | `/users/:id` | Actualizar datos personales |
| `GET` | `/users/:id/preferences` | Obtener preferencias de interfaz |
| `PATCH` | `/users/:id/preferences` | Actualizar gustos: música, fondo, modo oscuro, etc. |

## 🧠 Diagnostics Module
Formulario inicial de diagnóstico (para perfilar el tipo de estudiante).

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/diagnostics` | Enviar respuestas del formulario inicial |
| `GET` | `/diagnostics/:userId` | Obtener diagnóstico previo |
| `PUT` | `/diagnostics/:id` | Actualizar diagnóstico |

## 🧭 Recommendations Module
Generación de herramientas y metodologías recomendadas según diagnóstico.

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/recommendations/:userId` | Obtener recomendaciones personalizadas |
| `POST` | `/recommendations/custom` | Guardar una recomendación manual |
| `GET` | `/recommendations/tools` | Listar herramientas disponibles |
| `GET` | `/recommendations/methodologies` | Listar metodologías sugeridas |


## 🧩 Study Tools Module
Herramientas interactivas de estudio (**Flashcards**, **Temporizador Pomodoro**, **Cronómetro**, **Cuenta Regresiva** y **Notas**).

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/study/flashcards` | **Crear** nueva *flashcard*. |
| `GET` | `/study/flashcards/:userId` | **Listar** todas las *flashcards* del usuario. |
| `PATCH` | `/study/flashcards/:id` | **Actualizar** una *flashcard* existente. |
| `DELETE` | `/study/flashcards/:id` | **Eliminar** una *flashcard*. |
| `POST` | `/study/notes` | **Crear** una nueva nota de estudio. |
| `GET` | `/study/notes/:userId` | **Listar** todas las notas del usuario. |
| `PATCH` | `/study/notes/:id` | **Actualizar** el contenido de una nota. |
| `POST` | `/study/timer/pomodoro/start` | **Iniciar** un temporizador Pomodoro (con tiempo **personalizable**). |
| `POST` | `/study/timer/stopwatch/start` | **Iniciar** el **cronómetro** (*stopwatch*). |
| `POST` | `/study/timer/countdown/start` | **Iniciar** la cuenta regresiva. |
| `GET` | `/study/timer/countdown/recommended` | **Obtener tiempo recomendado** de estudio basado en sesiones previas. |
| `POST` | `/study/timer/stop` | **Detener/Pausar** cualquier temporizador activo (Pomodoro, Cronómetro o Cuenta Regresiva). |
| `POST` | `/study/session` | **Registrar** la sesión de estudio finalizada. |
| `GET` | `/study/sessions/:userId` | **Historial** de sesiones de estudio registradas. |

## 💬 Community Module
Interacción social y motivacional: publicaciones, like, imágenes, carrusel.

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/community/posts` | Crear publicación |
| `GET` | `/community/posts` | Listar publicaciones |
| `POST` | `/community/posts/:id/like` | Dar “like” a una publicación |
| `DELETE` | `/community/posts/:id/like` | Quitar “like” |
| `POST` | `/community/upload` | Subir imagen (usando Cloudinary o S3) |
| `GET` | `/community/carousel` | Listar imágenes del carrusel comunitario |

## 📊 Progress Module
Seguimiento de progreso de usuario.

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/progress/:userId` | Ver progreso (tiempo, módulos completados) |
| `POST` | `/progress` | Registrar nueva métrica de progreso |
| `GET` | `/progress/summary/:userId` | Resumen total (promedios, nivel de constancia) |

## 🎨 Personalization Module
Configuración estética y motivacional del entorno de estudio.

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/personalization/:userId` | Obtener configuración actual |
| `PATCH` | `/personalization/:userId` | Actualizar tema, fondo, música, colores, etc. |
| `GET` | `/personalization/themes` | Listar temas predefinidos |
| `POST` | `/personalization/themes/custom` | Guardar tema personalizado |



---

# 💾 ENTIDADES BASE (MODELOS PRISMA)

- `User`
- `Diagnostic`
- `Recommendation`
- `Flashcard`
- `StudySession`
- `Post`
- `Like`
- `Preference`


# MODELADO BASE DE DATOS


*Cada entidad se relacionará con `userId` para trazabilidad individual.*
