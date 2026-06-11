/**
 * Canales de WebSocket del sistema. Coinciden con las routing keys de RabbitMQ
 * (ws.chat, ws.support, ...) y con los paths del front (/ws/chat, ...).
 */
export type Channel = 'chat' | 'support' | 'session' | 'sensors' | 'notifications'

/** A quién entregar un evento: por usuario (seguro) o por sala (broadcast). */
export interface EventTarget {
  users?: number[]
  room?: string
}

/**
 * Sobre que el backend de negocio publica en RabbitMQ.
 * `data` es EXACTAMENTE lo que recibe el navegador (no se transforma).
 */
export interface EventEnvelope {
  channel: Channel
  target: EventTarget
  data: Record<string, unknown> // { type: "message:new", ... }
}
