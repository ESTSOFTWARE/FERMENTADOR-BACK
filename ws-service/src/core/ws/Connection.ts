import type { WebSocket } from 'ws'
import type { Channel } from '../events/EventEnvelope'

/** Una conexión WebSocket autenticada y activa. */
export interface Connection {
  id:        string      // id único de la conexión (para limpieza)
  userId:    number
  role:      string      // admin | profesor | estudiante | soporte
  sid:       string      // sesión única
  channel:   Channel
  socket:    WebSocket
  userName?: string      // se cachea perezosamente (ej. para el typing del chat)
}
