import { config } from './core/config/env'
import { createPool } from './core/db/pool'
import { PgSessionRepository } from './core/db/PgSessionRepository'
import { JwtTokenVerifier } from './core/auth/JwtTokenVerifier'
import { InMemoryConnectionRegistry } from './core/ws/InMemoryConnectionRegistry'
import { SocketServer } from './core/ws/SocketServer'
import { HandleConnection } from './core/ws/HandleConnection'
import { HandleDisconnect } from './core/ws/HandleDisconnect'
import { DeliverEvent } from './core/delivery/DeliverEvent'
import { RabbitMQEventBus } from './core/events/RabbitMQEventBus'

// Features: canales simples exportan un descriptor; chat/support son factories
// porque su typing necesita consultar la BD.
import { sessionChannel } from './features/session/infrastructure/session.channel'
import { notificationsChannel } from './features/notifications/infrastructure/notifications.channel'
import { sensorsChannel } from './features/sensors/infrastructure/sensors.channel'
import { createChatChannel } from './features/chat/infrastructure/chat.channel'
import { PgChatTypingRepository } from './features/chat/infrastructure/PgChatTypingRepository'
import { createSupportChannel } from './features/support/infrastructure/support.channel'
import { PgSupportTypingRepository } from './features/support/infrastructure/PgSupportTypingRepository'

export interface App {
  start(): Promise<void>
  stop(): Promise<void>
}

/**
 * Composition root: arma el core, registra los features y devuelve un App
 * con start/stop. Aquí (y solo aquí) se conecta lo externo (BD, RabbitMQ).
 */
export function createApp(): App {
  const pool     = createPool()
  const verifier = new JwtTokenVerifier(config.jwt.secret, config.jwt.algorithm)
  const sessions = new PgSessionRepository(pool)
  const registry = new InMemoryConnectionRegistry()
  const bus      = new RabbitMQEventBus(config.rabbitmq.url, config.rabbitmq.exchange)

  const handleConnection = new HandleConnection(verifier, sessions, registry)
  const handleDisconnect = new HandleDisconnect(registry)
  const deliverEvent     = new DeliverEvent(registry)

  const channels = [
    sessionChannel,
    notificationsChannel,
    sensorsChannel,
    createChatChannel(new PgChatTypingRepository(pool), deliverEvent),
    createSupportChannel(new PgSupportTypingRepository(pool), deliverEvent),
  ]

  const server = new SocketServer(registry, handleConnection, handleDisconnect, channels)

  return {
    async start() {
      server.listen(config.port)
      try {
        await bus.subscribe((event) => deliverEvent.execute(event))
        console.info('[WS] suscrito a RabbitMQ → entregando eventos')
      } catch (err) {
        console.error('[WS] RabbitMQ no disponible; el servidor sigue, sin entrega de eventos:', (err as Error).message)
      }
    },
    async stop() {
      await bus.close().catch(() => {})
      await pool.end().catch(() => {})
    },
  }
}
