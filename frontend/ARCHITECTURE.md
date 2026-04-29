# Frontend Architecture

La interfaz usa una organizacion por capas visuales:

- `app/`: rutas Next.js y composicion de paginas.
- `features/`: funcionalidades de negocio (`dane`, `inventory`).
- `shared/`: UI base, utilidades, tipos y contratos reutilizables.
- `widgets/`: piezas de layout de alto nivel como shell, sidebar y headers.
- `tests/`: pruebas unitarias y E2E.

Esta estructura permite que DANE, monitor y futuras vistas evolucionen sin mezclar tablas, API, diseño y dominio en un solo archivo.
