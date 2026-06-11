import type { ChannelDescriptor } from '../../../core/ws/ChannelDescriptor'
import type { DeliverEvent } from '../../../core/delivery/DeliverEvent'
import type { ChatTypingRepository } from '../domain/ChatTypingRepository'
import { RelayChatTyping } from '../application/RelayChatTyping'

/**
 * /ws/chat — chat entre docentes/alumnos.
 * Entrega de mensajes: vía RabbitMQ (el back publica). typing: relay local aquí.
 */
export function createChatChannel(repo: ChatTypingRepository, deliver: DeliverEvent): ChannelDescriptor {
  const relayTyping = new RelayChatTyping(repo, deliver)
  return {
    channel: 'chat',
    path:    'chat',
    onClientMessage: (conn, data) => relayTyping.execute(conn, data),
  }
}
