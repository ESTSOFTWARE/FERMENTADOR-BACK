import type { Connection } from '../../../core/ws/Connection'
import type { DeliverEvent } from '../../../core/delivery/DeliverEvent'
import type { ChatTypingRepository } from '../domain/ChatTypingRepository'

/**
 * Reenvía el "está escribiendo" del chat a los demás miembros de la conversación
 * (paridad exacta con el back actual). El cliente envía typing:start/stop con
 * conversationId; se valida membresía y se entrega a los otros miembros con el
 * nombre del usuario. El nombre se cachea en la conexión (no se consulta cada tecla).
 *
 * La entrega es local (a los sockets de esta instancia). El typing es efímero,
 * así que en multi-instancia no se propaga entre nodos — aceptable.
 */
export class RelayChatTyping {
  constructor(
    private readonly repo: ChatTypingRepository,
    private readonly deliver: DeliverEvent,
  ) {}

  async execute(conn: Connection, data: Record<string, unknown>): Promise<void> {
    const type = data.type
    if (type !== 'typing:start' && type !== 'typing:stop') return

    const conversationId = data.conversationId
    if (typeof conversationId !== 'number') return

    if (!(await this.repo.isMember(conversationId, conn.userId))) return

    const memberIds = await this.repo.getMemberIds(conversationId)
    const others    = memberIds.filter((id) => id !== conn.userId)
    if (others.length === 0) return

    if (conn.userName === undefined) {
      conn.userName = await this.repo.getUserName(conn.userId)
    }

    this.deliver.execute({
      channel: 'chat',
      target:  { users: others },
      data: {
        type:           'typing',
        conversationId,
        userId:         conn.userId,
        userName:       conn.userName,
        typing:         type === 'typing:start',
      },
    })
  }
}
