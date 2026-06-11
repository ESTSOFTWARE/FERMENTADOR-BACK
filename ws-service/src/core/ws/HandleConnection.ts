import { randomUUID } from 'node:crypto'
import type { WebSocket } from 'ws'
import type { Connection } from './Connection'
import type { Channel } from '../events/EventEnvelope'
import type { ConnectionRegistry } from './ConnectionRegistry'
import type { TokenVerifier } from '../auth/TokenVerifier'
import type { SessionRepository } from '../db/SessionRepository'
import { UnauthorizedError } from '../errors'

/**
 * Autentica un handshake WebSocket (mismo flujo que el backend actual):
 *   1. Verifica el JWT de la cookie.
 *   2. Valida la sesión única (sid == active_session_id en BD).
 *   3. Registra la conexión.
 * Lanza UnauthorizedError si algo falla → el server cierra con 4401.
 */
export class HandleConnection {
  constructor(
    private readonly verifier: TokenVerifier,
    private readonly sessions: SessionRepository,
    private readonly registry: ConnectionRegistry,
  ) {}

  async execute(token: string | undefined, channel: Channel, socket: WebSocket): Promise<Connection> {
    if (!token) throw new UnauthorizedError('missing token')

    const claims = this.verifier.verify(token)

    const active = await this.sessions.getActiveSessionId(claims.userId)
    if (!claims.sid || claims.sid !== active) {
      throw new UnauthorizedError('session replaced')
    }

    const conn: Connection = {
      id:      randomUUID(),
      userId:  claims.userId,
      role:    claims.role,
      sid:     claims.sid,
      channel,
      socket,
    }
    this.registry.add(conn)
    return conn
  }
}
