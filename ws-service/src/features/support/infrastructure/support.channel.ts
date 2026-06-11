import type { ChannelDescriptor } from '../../../core/ws/ChannelDescriptor'
import type { DeliverEvent } from '../../../core/delivery/DeliverEvent'
import type { SupportTypingRepository } from '../domain/SupportTypingRepository'
import { RelaySupportTyping } from '../application/RelaySupportTyping'

/**
 * /ws/support-chat — chat admin ↔ soporte.
 * Entrega de mensajes: vía RabbitMQ (el back publica). typing: relay local aquí.
 */
export function createSupportChannel(repo: SupportTypingRepository, deliver: DeliverEvent): ChannelDescriptor {
  const relayTyping = new RelaySupportTyping(repo, deliver)
  return {
    channel: 'support',
    path:    'support-chat',
    onClientMessage: (conn, data) => relayTyping.execute(conn, data),
  }
}
