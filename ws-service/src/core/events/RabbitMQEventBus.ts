import amqp from 'amqplib'
import type { EventBus } from './EventBus'
import type { EventEnvelope } from './EventEnvelope'

const RETRY_DELAY_MS = 5_000

/**
 * Consume los sobres que el backend publica en el exchange "ws.events"
 * (topic, routing keys ws.chat / ws.support / ...). Cola exclusiva por
 * instancia bound a "ws.#" → todas las instancias reciben cada evento.
 * Reconecta automáticamente si RabbitMQ cierra la conexión (heartbeat
 * timeout, reinicio del broker, etc.).
 */
export class RabbitMQEventBus implements EventBus {
  private connection?: amqp.ChannelModel
  private channel?: amqp.Channel
  private onEvent?: (event: EventEnvelope) => void
  private closing = false

  constructor(
    private readonly url: string,
    private readonly exchange: string,
  ) {}

  async subscribe(onEvent: (event: EventEnvelope) => void): Promise<void> {
    this.onEvent = onEvent
    await this._connect()
  }

  private async _connect(): Promise<void> {
    try {
      this.connection = await amqp.connect(this.url)
      this.channel = await this.connection.createChannel()

      // Evitar que un error no manejado tumbe el proceso
      this.connection.on('error', (err) => {
        console.error('[RabbitMQ] error de conexión:', err.message)
      })
      this.connection.on('close', () => {
        if (!this.closing) {
          console.warn(`[RabbitMQ] conexión cerrada, reconectando en ${RETRY_DELAY_MS / 1000}s…`)
          setTimeout(() => this._connect(), RETRY_DELAY_MS)
        }
      })

      await this.channel.assertExchange(this.exchange, 'topic', { durable: true })
      const { queue } = await this.channel.assertQueue('', { exclusive: true })
      await this.channel.bindQueue(queue, this.exchange, 'ws.#')

      await this.channel.consume(queue, (msg) => {
        if (!msg) return
        try {
          const event = JSON.parse(msg.content.toString()) as EventEnvelope
          this.onEvent?.(event)
        } catch {
          // sobre malformado: lo descartamos sin tumbar el consumer
        }
        this.channel?.ack(msg)
      })

      console.info('[RabbitMQ] conectado y escuchando eventos')
    } catch (err) {
      if (!this.closing) {
        console.error(`[RabbitMQ] no se pudo conectar, reintentando en ${RETRY_DELAY_MS / 1000}s…`, err)
        setTimeout(() => this._connect(), RETRY_DELAY_MS)
      }
    }
  }

  async close(): Promise<void> {
    this.closing = true
    await this.channel?.close()
    await this.connection?.close()
  }
}
