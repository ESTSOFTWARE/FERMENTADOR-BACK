import type { Channel } from '../events/EventEnvelope'
import type { Connection } from './Connection'
import type { ConnectionRegistry } from './ConnectionRegistry'

export interface PresenceContext {
  registry: ConnectionRegistry
}

/**
 * Descriptor de un canal WebSocket. Cada feature (session, chat, sensors, ...)
 * exporta uno; el core lo usa para enrutar, unir salas y manejar mensajes
 * cliente→servidor — sin que el core conozca la lógica de cada canal.
 */
export interface ChannelDescriptor {
  /** Nombre del canal (coincide con la routing key de RabbitMQ). */
  channel: Channel
  /** Segmento del path tras /ws/  (ej: "session", "support-chat", "sensors"). */
  path: string
  /** Deriva una sala de los segmentos extra del path (ej: /ws/sensors/12 → "circuit:12"). */
  roomFromParams?: (params: string[]) => string | null
  /** Maneja mensajes que el cliente envía por el socket (ej: typing). Opcional. */
  onClientMessage?: (conn: Connection, data: Record<string, unknown>) => void | Promise<void>
  /** Llamado justo después de que la conexión queda registrada. */
  onConnect?: (conn: Connection, ctx: PresenceContext) => void | Promise<void>
  /** Llamado justo después de que la conexión es eliminada del registro. */
  onDisconnect?: (conn: Connection, ctx: PresenceContext) => void | Promise<void>
}
