import { WebSocket } from 'ws'
import type { Connection } from '../ws/Connection'
import type { EventEnvelope } from '../events/EventEnvelope'
import type { ConnectionRegistry } from '../ws/ConnectionRegistry'

/**
 * Entrega un evento (sobre de RabbitMQ) a sus destinatarios.
 * El `data` se envía TAL CUAL al navegador — sin transformar.
 */
export class DeliverEvent {
  constructor(private readonly registry: ConnectionRegistry) {}

  execute(event: EventEnvelope): void {
    const payload = JSON.stringify(event.data)

    let targets: Connection[] = []
    if (event.target.users && event.target.users.length > 0) {
      const seen = new Set<string>()
      for (const userId of event.target.users) {
        for (const conn of this.registry.getByUser(userId)) {
          if (!seen.has(conn.id)) { seen.add(conn.id); targets.push(conn) }
        }
      }
    } else if (event.target.room) {
      targets = this.registry.getByRoom(event.target.room)
    }

    for (const conn of targets) {
      if (conn.socket.readyState === WebSocket.OPEN) {
        conn.socket.send(payload)
      }
    }
  }
}
