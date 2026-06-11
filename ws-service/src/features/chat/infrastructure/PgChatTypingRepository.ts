import type { Pool } from 'pg'
import type { ChatTypingRepository } from '../domain/ChatTypingRepository'

/** Consulta membresía del chat y nombre del usuario en PostgreSQL. */
export class PgChatTypingRepository implements ChatTypingRepository {
  constructor(private readonly pool: Pool) {}

  async isMember(conversationId: number, userId: number): Promise<boolean> {
    const res = await this.pool.query(
      'SELECT 1 FROM chat_conversation_members WHERE conversation_id = $1 AND user_id = $2 LIMIT 1',
      [conversationId, userId],
    )
    return (res.rowCount ?? 0) > 0
  }

  async getMemberIds(conversationId: number): Promise<number[]> {
    const res = await this.pool.query<{ user_id: number }>(
      'SELECT user_id FROM chat_conversation_members WHERE conversation_id = $1',
      [conversationId],
    )
    return res.rows.map((r) => r.user_id)
  }

  async getUserName(userId: number): Promise<string> {
    const res = await this.pool.query<{ name: string; last_name: string }>(
      'SELECT name, last_name FROM users WHERE id = $1',
      [userId],
    )
    const row = res.rows[0]
    if (!row) return 'Usuario'
    return `${row.name} ${row.last_name}`.trim() || 'Usuario'
  }
}
