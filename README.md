# DAWFILMS

**Autor:** [Jesús Jiménez Pérez]  
**Tutor:** [Jose Manuel Rivas García]  
**I.E.S. Francisco Romero Vargas (Jerez de la Frontera)**  
**Desarrollo de aplicaciones web**  
**Curso:** 2024/2025
> [!WARNING]
> Para la versión completa de la documentación ver el pdf
---

## Tabla de contenido

1. [Introducción](#introducción)
2. [Finalidad](#finalidad)
3. [Objetivos](#objetivos)
4. [Medios necesarios](#medios-necesarios)
5. [Realización del Proyecto](#realización-del-proyecto)
6. [Trabajos realizados](#trabajos-realizados)

---

## Introducción

Este proyecto consiste en el desarrollo de una plataforma web para la gestión y descubrimiento de películas, que incluye un sistema de chat en tiempo real entre usuarios y un bot inteligente para recomendaciones cinematográficas. La aplicación web permite a los usuarios buscar películas, gestionar listas de favoritos y pendientes de ver, escribir reseñas, y mantener conversaciones con otros usuarios o con un bot especializado en cine.

El sistema está construido sobre Django como framework principal, utiliza la API de The Movie Database (TMDB) para obtener información actualizada de películas, implementa WebSockets para el chat en tiempo real, y se integra con Rasa para proporcionar un bot conversacional inteligente.

## Finalidad

La finalidad de este proyecto es crear una comunidad online de amantes del cine donde los usuarios puedan:

- Descubrir nuevas películas a través de un catálogo actualizado y sistema de búsqueda
- Gestionar sus preferencias cinematográficas con listas personalizadas
- Compartir opiniones mediante un sistema de reseñas y valoraciones
- Conectar con otros usuarios que compartan gustos similares
- Recibir recomendaciones personalizadas a través de un asistente virtual inteligente
- Mantener conversaciones en tiempo real sobre películas y temas relacionados

El proyecto busca mejorar la experiencia cinematográfica del usuario, eliminando la necesidad de usar múltiples plataformas para diferentes funcionalidades relacionadas con el cine.

## Objetivos

Los objetivos técnicos específicos de este proyecto son:

1. **Desarrollo de una aplicación web completa** utilizando Django como framework principal
2. **Integración con API externa** para obtener datos actualizados de películas desde TMDB
3. **Implementación de sistema de autenticación** con perfiles de usuario personalizables
4. **Creación de funcionalidades de gestión de contenido** (favoritos, watchlist, reseñas)
5. **Desarrollo de sistema de chat en tiempo real** usando WebSockets y Django Channels
6. **Implementación de sistema de amistad** entre usuarios
7. **Integración de bot conversacional** utilizando Rasa para procesamiento de lenguaje natural
8. **Desarrollo de interfaz responsive** para uso en diferentes dispositivos
9. **Implementación de filtros de contenido** según preferencias del usuario
10. **Creación de sistema de notificaciones** para mensajes no leídos

## Medios necesarios

Para la realización de este proyecto se necesita lo siguiente:

### Hardware
- Ordenador de desarrollo
- Conexión a internet estable para consultas a APIs externas
- Servidor web para el despliegue (AWS)

### Software
- **Sistema Operativo:** Linux/Windows
- **Lenguaje de programación:** Python
- **Framework web:** Django
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **Servidor web:** Nginx + Gunicorn
- **WebSockets:** Django Channels con Redis
- **Bot framework:** Rasa
- **Control de versiones:** Git
- **Editor de código:** Visual Studio Code y PyCharm

### APIs y Servicios Externos
- **The Movie Database (TMDB) API:** Para datos de películas
- **Redis:** Para el manejo de WebSockets y cache
- **Rasa:** Para el procesamiento de lenguaje natural del bot

### Librerías Python principales
- Django, Django Channels
- Requests (para llamadas a API)
- Rasa, Rasa SDK
- Redis, channels-redis
- Pillow (para manejo de imágenes)

## Realización del Proyecto

### Trabajos realizados

El desarrollo del proyecto se ha llevado a cabo siguiendo la metodología de desarrollo kanban, implementando funcionalidades de forma incremental y realizando pruebas continuas.

#### 1. Estructura del proyecto
Se ha creado una aplicación Django modular con las siguientes funcionalidades:
- **auth:** Manejo de autenticación y perfiles de usuario
- **films:** Gestión de películas, favoritos, reseñas y watchlist
- **chat:** Sistema de mensajería y amistad entre usuarios
- **tmdb_management:** Integración con la API de TMDB

#### 2. Integración con TMDB API
Se ha desarrollado una clase `TMDBApi` que encapsula todas las llamadas a la API externa:
- Obtención de películas populares
- Sistema de búsqueda de películas
- Detalles completos de películas individuales
- Información de reparto y equipo técnico
- Videos y trailers asociados
- Recomendaciones basadas en películas

#### 3. Sistema de gestión de usuarios
Implementación completa de:
- Registro y autenticación de usuarios
- Perfiles personalizables con avatares
- Preferencias de contenido (filtrado de contenido adulto)
- Sistema de favoritos y lista de películas por ver
- Reseñas y valoraciones personales

#### 4. Sistema de chat en tiempo real
Desarrollo de un sistema de mensajería completo:
- Chat bidireccional entre usuarios amigos
- Indicadores de estado en tiempo real (escribiendo, conectado)
- Sistema de amistad con solicitudes y aceptaciones
- Historial de conversaciones persistente
- Notificaciones de mensajes no leídos

#### 5. Bot conversacional inteligente
Integración de un bot especializado en cine:
- Procesamiento de lenguaje natural con Rasa
- Respuestas contextualmente relevantes
- Integración seamless con el sistema de chat
- Capacidad de proporcionar recomendaciones personalizadas

---


