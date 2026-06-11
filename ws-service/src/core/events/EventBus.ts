import type { EventEnvelope } from './EventEnvelope'

/** Bus de eventos entrantes (RabbitMQ). El servicio se suscribe y entrega. */
export interface EventBus {
  subscribe(onEvent: (event: EventEnvelope) => void): Promise<void>
  close(): Promise<void>
}
