import amqp from 'amqplib'
import type { EventBus } from './EventBus'
import type { EventEnvelope } from './EventEnvelope'

/**
 * Consume los sobres que el backend publica en el exchange "ws.events"
 * (topic, routing keys ws.chat / ws.support / ...). Cola exclusiva por
 * instancia bound a "ws.#" → todas las instancias reciben cada evento.
 */
export class RabbitMQEventBus implements EventBus {
  private connection?: amqp.ChannelModel
  private channel?: amqp.Channel

  constructor(
    private readonly url: string,
    private readonly exchange: string,
  ) {}

  async subscribe(onEvent: (event: EventEnvelope) => void): Promise<void> {
    this.connection = await amqp.connect(this.url)
    this.channel = await this.connection.createChannel()

    await this.channel.assertExchange(this.exchange, 'topic', { durable: true })
    const { queue } = await this.channel.assertQueue('', { exclusive: true })
    await this.channel.bindQueue(queue, this.exchange, 'ws.#')

    await this.channel.consume(queue, (msg) => {
      if (!msg) return
      try {
        const event = JSON.parse(msg.content.toString()) as EventEnvelope
        onEvent(event)
      } catch {
        // sobre malformado: lo descartamos sin tumbar el consumer
      }
      this.channel?.ack(msg)
    })
  }

  async close(): Promise<void> {
    await this.channel?.close()
    await this.connection?.close()
  }
}
