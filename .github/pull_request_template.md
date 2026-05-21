## Descripción

<!-- Explica qué hace este PR y por qué es necesario -->

## Tipo de cambio

- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Refactor
- [ ] Documentación
- [ ] Otro: ___

## Cambios realizados

<!--
Lista los archivos o módulos principales que se modificaron y qué se hizo en cada uno.
Ejemplo:
- `src/core/models/user_models.py` — Se agregó el campo `is_active`
- `src/services/auth/...` — Se modificó el flujo OAuth para reactivar cuentas
-->

## ¿Cómo probarlo?

<!--
Pasos para verificar que el cambio funciona correctamente.
Ejemplo:
1. Crear un usuario con OAuth
2. Esperar o simular los 30 días sin vincular circuito
3. Verificar que la cuenta se desactiva
4. Volver a hacer OAuth y verificar que la cuenta se reactiva
-->

## Checklist

- [ ] El código pasa `ruff check .`
- [ ] Se agregaron o actualizaron pruebas si aplica
- [ ] No se introducen regresiones en funcionalidades existentes
- [ ] Los cambios en BD están reflejados en `init.sql`
- [ ] Se documentaron decisiones de diseño no obvias en el código
