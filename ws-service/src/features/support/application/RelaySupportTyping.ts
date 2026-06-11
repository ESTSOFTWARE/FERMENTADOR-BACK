import type { Connection } from '../../../core/ws/Connection'
import type { DeliverEvent } from '../../../core/delivery/DeliverEvent'
import type { SupportTypingRepository } from '../domain/SupportTypingRepository'

/**
 * Reenvía el "está escribiendo" del chat de soporte (paridad con el back actual).
 * Destinatarios = admin dueño de la conversación + agentes de soporte, menos el
 * emisor. El admin solo puede escribir en SU propia conversación.
 */
export class RelaySupportTyping {
  constructor(
    private readonly repo: SupportTypingRepository,
    private readonly deliver: DeliverEvent,
  ) {}

  async execute(conn: Connection, data: Record<string, unknown>): Promise<void> {
    const type = data.type
    if (type !== 'typing:start' && type !== 'typing:stop') return

    const conversationId = data.conversationId
    if (typeof conversationId !== 'number') return

    const adminId = await this.repo.getAdminId(conversationId)
    if (adminId === null) return

    // El admin solo puede "escribir" en su propia conversación.
    if (conn.role === 'admin' && adminId !== conn.userId) return

    const agents = await this.repo.getSupportAgentIds()
    const others = [...new Set([adminId, ...agents])].filter((id) => id !== conn.userId)
    if (others.length === 0) return

    this.deliver.execute({
      channel: 'support',
      target:  { users: others },
      data: {
        type:           'typing',
        conversationId,
        userId:         conn.userId,
        role:           conn.role,
        typing:         type === 'typing:start',
      },
    })
  }
}
