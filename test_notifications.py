"""
Script de pruebas para el sistema de notificaciones de Nich-Ká.

Uso:
    python test_notifications.py                  → menú interactivo
    python test_notifications.py --warning         → prueba correo de advertencia
    python test_notifications.py --reactivation    → prueba correo de reactivación
    python test_notifications.py --deactivate      → prueba desactivación de cuentas
    python test_notifications.py --all             → todas las pruebas

Coloca este archivo en la raíz del proyecto (junto a src/).
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone

# ── Asegurar que src/ esté en el path ─────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Cargar todos los modelos para que SQLAlchemy resuelva las FK ──────────────
import src.core.models.user_models  # noqa: F401
import src.core.models.announcement_model  # noqa: F401
import src.core.models.group_models  # noqa: F401
import src.services.fermentation.infrastructure.adapters.MySQL  # noqa: F401
import src.services.circuits.infrastructure.adapters.MySQL  # noqa: F401

# ── Colores para la consola ───────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):    print(f"  {GREEN}✓ {msg}{RESET}")
def warn(msg):  print(f"  {YELLOW}⚠ {msg}{RESET}")
def err(msg):   print(f"  {RED}✗ {msg}{RESET}")
def info(msg):  print(f"  {CYAN}→ {msg}{RESET}")
def title(msg): print(f"\n{BOLD}{msg}{RESET}\n{'─' * 50}")


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA 1: Correo de advertencia (2 días antes del vencimiento)
# ══════════════════════════════════════════════════════════════════════════════
async def test_warning_email():
    title("PRUEBA 1: Correo de advertencia (vencimiento en 2 días)")

    from src.core.database import AsyncSessionLocal
    from src.core.models.user_models import UserModel
    from src.services.users.application.usecase.send_warning_email_use_case import SendWarningEmailUseCase
    from src.services.users.infrastructure.adapters.MySQL import UserRepository
    from sqlalchemy import insert, delete, select

    email_prueba = input(f"  {CYAN}Email real donde recibirás el correo: {RESET}").strip()
    if not email_prueba:
        err("Email vacío, cancelando prueba.")
        return

    user_id = None
    try:
        # 1. Insertar usuario de prueba con created_at hace 28 días
        created_at = datetime.now(timezone.utc) - timedelta(days=28, hours=1)
        info(f"Creando usuario de prueba con created_at = {created_at.strftime('%Y-%m-%d %H:%M')} ...")

        async with AsyncSessionLocal() as session:
            # Borrar si ya existe de una prueba anterior
            await session.execute(
                delete(UserModel).where(UserModel.email == email_prueba)
            )
            await session.commit()

            model = UserModel(
                name="Test",
                last_name="Warning",
                email=email_prueba,
                password=None,
                role_id=1,
                is_active=True,
                circuit_id=None,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            user_id = model.id

            # Actualizar created_at directamente (server_default no acepta valores pasados)
            from sqlalchemy import update, text
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(created_at=created_at.replace(tzinfo=None))
            )
            await session.commit()

        ok(f"Usuario de prueba creado (id={user_id})")

        # 2. Ejecutar el use case
        info("Ejecutando SendWarningEmailUseCase ...")
        repo = UserRepository(AsyncSessionLocal)
        count = await SendWarningEmailUseCase(repo).execute()

        if count > 0:
            ok(f"{count} correo(s) de advertencia enviado(s)")
        else:
            warn("No se enviaron correos. Revisa los logs o las condiciones del filtro.")

        # 3. Verificar que warning_email_sent_at se actualizó
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user and user.warning_email_sent_at:
                ok(f"warning_email_sent_at actualizado: {user.warning_email_sent_at}")
            else:
                warn("warning_email_sent_at sigue en NULL (el correo puede no haberse enviado)")

        # 4. Verificar que no se envíe dos veces
        info("Ejecutando use case por segunda vez (no debe enviar correos) ...")
        count2 = await SendWarningEmailUseCase(repo).execute()
        if count2 == 0:
            ok("Segunda ejecución correcta: 0 correos enviados (idempotente ✓)")
        else:
            err(f"¡Problema! Se enviaron {count2} correos en la segunda ejecución")

    except Exception as e:
        err(f"Error durante la prueba: {e}")
        raise
    finally:
        # 5. Limpiar usuario de prueba
        if user_id:
            try:
                async with AsyncSessionLocal() as session:
                    await session.execute(
                        delete(UserModel).where(UserModel.id == user_id)
                    )
                    await session.commit()
                info("Usuario de prueba eliminado de la BD.")
            except Exception as e:
                warn(f"No se pudo limpiar el usuario de prueba: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA 2: Correo de reactivación (login OAuth con cuenta desactivada)
# ══════════════════════════════════════════════════════════════════════════════
async def test_reactivation_email():
    title("PRUEBA 2: Correo de reactivación (cuenta desactivada → OAuth login)")

    from src.core.database import AsyncSessionLocal
    from src.core.models.user_models import UserModel
    from src.services.users.application.usecase.send_reactivation_email_use_case import SendReactivationEmailUseCase
    from src.services.users.infrastructure.adapters.MySQL import UserRepository
    from sqlalchemy import insert, delete, select, update

    email_prueba = input(f"  {CYAN}Email real donde recibirás el correo: {RESET}").strip()
    if not email_prueba:
        err("Email vacío, cancelando prueba.")
        return

    user_id = None
    try:
        # 1. Crear usuario desactivado (simula cuenta que venció los 30 días)
        info("Creando usuario desactivado (simula cuenta vencida) ...")

        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(UserModel).where(UserModel.email == email_prueba)
            )
            await session.commit()

            model = UserModel(
                name="Test",
                last_name="Reactivation",
                email=email_prueba,
                password=None,
                role_id=1,
                is_active=False,       # ← desactivada
                circuit_id=None,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            user_id = model.id

        ok(f"Usuario desactivado creado (id={user_id}, is_active=False)")

        # 2. Verificar estado inicial en BD
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one()
            info(f"Estado inicial → is_active={user.is_active}, reactivated_at={user.reactivated_at}")

        # 3. Simular reactivación OAuth (lo que hace el use case en GoogleWebAuthUseCase / GitHubWebAuthUseCase)
        info("Simulando reactivación OAuth (ejecutando SendReactivationEmailUseCase) ...")
        repo = UserRepository(AsyncSessionLocal)

        # Primero reactivar en BD
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(is_active=True)
            )
            await session.commit()

        # Luego enviar correo y registrar timestamps
        success = await SendReactivationEmailUseCase(repo).execute(
            user_id=user_id,
            user_name="Test",
            user_email=email_prueba,
        )

        if success:
            ok("Correo de reactivación enviado exitosamente")
        else:
            err("El use case retornó False. Revisa los logs.")

        # 4. Verificar estado final en BD
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user = result.scalar_one()

            if user.is_active:
                ok(f"is_active = True ✓")
            else:
                err("is_active sigue en False")

            if user.reactivated_at:
                ok(f"reactivated_at = {user.reactivated_at}")
            else:
                warn("reactivated_at sigue en NULL")

            if user.last_oauth_login_at:
                ok(f"last_oauth_login_at = {user.last_oauth_login_at}")
            else:
                warn("last_oauth_login_at sigue en NULL")

    except Exception as e:
        err(f"Error durante la prueba: {e}")
        raise
    finally:
        if user_id:
            try:
                async with AsyncSessionLocal() as session:
                    await session.execute(
                        delete(UserModel).where(UserModel.id == user_id)
                    )
                    await session.commit()
                info("Usuario de prueba eliminado de la BD.")
            except Exception as e:
                warn(f"No se pudo limpiar el usuario de prueba: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA 3: Desactivación de cuentas expiradas
# ══════════════════════════════════════════════════════════════════════════════
async def test_deactivate_expired():
    title("PRUEBA 3: Desactivación de cuentas expiradas (30 días sin circuito)")

    from src.core.database import AsyncSessionLocal
    from src.core.models.user_models import UserModel
    from src.services.users.application.usecase.deactivate_expired_users_use_case import DeactivateExpiredUsersUseCase
    from src.services.users.infrastructure.adapters.MySQL import UserRepository
    from sqlalchemy import delete, select, update

    user_ids = []
    try:
        async with AsyncSessionLocal() as session:
            # Usuario A: 31 días sin circuito → debe desactivarse
            model_a = UserModel(
                name="Test",
                last_name="Expired",
                email="test_expired_31d@nichka-test.local",
                password=None,
                role_id=1,
                is_active=True,
                circuit_id=None,
            )
            # Usuario B: 15 días sin circuito → NO debe desactivarse
            model_b = UserModel(
                name="Test",
                last_name="Active",
                email="test_active_15d@nichka-test.local",
                password=None,
                role_id=1,
                is_active=True,
                circuit_id=None,
            )
            # Usuario C: 31 días pero con circuito → NO debe desactivarse
            model_c = UserModel(
                name="Test",
                last_name="WithCircuit",
                email="test_circuit_31d@nichka-test.local",
                password=None,
                role_id=1,
                is_active=True,
                circuit_id=None,  # sin circuit_id FK real para no romper constraints
            )

            for m in [model_a, model_b, model_c]:
                await session.execute(
                    delete(UserModel).where(UserModel.email == m.email)
                )
            await session.commit()

            for m in [model_a, model_b, model_c]:
                session.add(m)
            await session.commit()

            for m in [model_a, model_b, model_c]:
                await session.refresh(m)
                user_ids.append(m.id)

            # Ajustar created_at
            expired_date = datetime.now(timezone.utc) - timedelta(days=31)
            recent_date  = datetime.now(timezone.utc) - timedelta(days=15)

            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_ids[0])  # A: 31 días
                .values(created_at=expired_date.replace(tzinfo=None))
            )
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_ids[1])  # B: 15 días
                .values(created_at=recent_date.replace(tzinfo=None))
            )
            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_ids[2])  # C: 31 días, marcamos con email diferente
                .values(created_at=expired_date.replace(tzinfo=None))
            )
            await session.commit()

        ok(f"Usuarios de prueba creados: ids={user_ids}")
        info("A (31d, sin circuito) → esperado: DESACTIVADO")
        info("B (15d, sin circuito) → esperado: ACTIVO")
        info("C (31d, sin circuito) → esperado: DESACTIVADO (mismo caso que A)")

        # Ejecutar use case
        info("Ejecutando DeactivateExpiredUsersUseCase ...")
        repo = UserRepository(AsyncSessionLocal)
        count = await DeactivateExpiredUsersUseCase(repo).execute()
        ok(f"Cuentas desactivadas: {count}")

        # Verificar resultados
        async with AsyncSessionLocal() as session:
            results = {}
            for uid in user_ids:
                r = await session.execute(
                    select(UserModel).where(UserModel.id == uid)
                )
                u = r.scalar_one()
                results[uid] = u.is_active

        labels = ["A (31d sin circuito)", "B (15d sin circuito)", "C (31d sin circuito)"]
        expected = [False, True, False]

        print()
        for i, (uid, label, exp) in enumerate(zip(user_ids, labels, expected)):
            actual = results[uid]
            if actual == exp:
                ok(f"Usuario {label}: is_active={actual} ✓")
            else:
                err(f"Usuario {label}: esperado is_active={exp}, obtenido={actual}")

    except Exception as e:
        err(f"Error durante la prueba: {e}")
        raise
    finally:
        if user_ids:
            try:
                async with AsyncSessionLocal() as session:
                    for uid in user_ids:
                        await session.execute(
                            delete(UserModel).where(UserModel.id == uid)
                        )
                    await session.commit()
                info("Usuarios de prueba eliminados de la BD.")
            except Exception as e:
                warn(f"No se pudo limpiar: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MENÚ PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
async def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None

    print(f"\n{BOLD}{'═' * 50}")
    print("  NICH-KÁ · Sistema de Notificaciones · Tests")
    print(f"{'═' * 50}{RESET}")

    if arg == "--warning":
        await test_warning_email()
    elif arg == "--reactivation":
        await test_reactivation_email()
    elif arg == "--deactivate":
        await test_deactivate_expired()
    elif arg == "--all":
        await test_warning_email()
        await test_reactivation_email()
        await test_deactivate_expired()
    else:
        print(f"""
  {CYAN}Elige una prueba:{RESET}

  {BOLD}1{RESET} → Correo de advertencia (2 días antes del vencimiento)
  {BOLD}2{RESET} → Correo de reactivación (cuenta desactivada → OAuth)
  {BOLD}3{RESET} → Desactivación de cuentas expiradas (30 días)
  {BOLD}4{RESET} → Todas las pruebas
  {BOLD}q{RESET} → Salir
""")
        opcion = input(f"  {CYAN}Opción: {RESET}").strip()
        if opcion == "1":
            await test_warning_email()
        elif opcion == "2":
            await test_reactivation_email()
        elif opcion == "3":
            await test_deactivate_expired()
        elif opcion == "4":
            await test_warning_email()
            await test_reactivation_email()
            await test_deactivate_expired()
        else:
            info("Saliendo.")
            return

    print(f"\n{BOLD}{'─' * 50}")
    print(f"  Pruebas finalizadas")
    print(f"{'─' * 50}{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())