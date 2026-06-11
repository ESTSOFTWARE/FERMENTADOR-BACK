import type { Connection } from './Connection'
import type { ConnectionRegistry } from './ConnectionRegistry'

/** Limpia una conexión cuando el socket se cierra. */
export class HandleDisconnect {
  constructor(private readonly registry: ConnectionRegistry) {}

  execute(conn: Connection): void {
    this.registry.remove(conn)
  }
}
