import { WebSocket } from 'ws'
import type { ChannelDescriptor, PresenceContext } from '../../../core/ws/ChannelDescriptor'
import type { Connection } from '../../../core/ws/Connection'
import type { DeliverEvent } from '../../../core/delivery/DeliverEvent'
import type { ChatTypingRepository } from '../domain/ChatTypingRepository'
import { RelayChatTyping } from '../application/RelayChatTyping'

function sendToUser(ctx: PresenceContext, userId: number, data: unknown): void {
  const payload = JSON.stringify(data)
  for (const c of ctx.registry.getByUser(userId)) {
    if (c.socket.readyState === WebSocket.OPEN) c.socket.send(payload)
  }
}

function sendDirect(conn: Connection, data: unknown): void {
  if (conn.socket.readyState === WebSocket.OPEN) {
    conn.socket.send(JSON.stringify(data))
  }
}

/**
 * /ws/chat — chat entre docentes/alumnos.
 * Entrega de mensajes: vía RabbitMQ (el back publica).
 * typing: relay local. Presencia: online/offline en tiempo real.
 */
export function createChatChannel(repo: ChatTypingRepository, deliver: DeliverEvent): ChannelDescriptor {
  const relayTyping = new RelayChatTyping(repo, deliver)
  return {
    channel: 'chat',
    path:    'chat',
    onClientMessage: (conn, data) => relayTyping.execute(conn, data),

    onConnect: async (conn, ctx) => {
      const chatableIds = await repo.getChatableUserIds(conn.userId)
      // Enviar al usuario recién conectado quiénes están online ahora
      const onlineNow = [...chatableIds].filter(id => ctx.registry.getByUser(id).length > 0)
      sendDirect(conn, { type: 'presence:init', onlineUserIds: onlineNow })
      // Notificar a contactos que este usuario se conectó
      for (const id of chatableIds) {
        sendToUser(ctx, id, { type: 'user:online', userId: conn.userId })
      }
    },

    onDisconnect: async (conn, ctx) => {
      // Solo avisar offline si ya no le quedan conexiones (multi-pestaña/dispositivo)
      if (ctx.registry.getByUser(conn.userId).length > 0) return
      const chatableIds = await repo.getChatableUserIds(conn.userId)
      for (const id of chatableIds) {
        sendToUser(ctx, id, { type: 'user:offline', userId: conn.userId })
      }
    },
  }
}
