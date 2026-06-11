import type { Pool } from 'pg'
import type { SupportTypingRepository } from '../domain/SupportTypingRepository'

/** Consulta el admin dueño de la conversación y los agentes de soporte en PostgreSQL. */
export class PgSupportTypingRepository implements SupportTypingRepository {
  constructor(private readonly pool: Pool) {}

  async getAdminId(conversationId: number): Promise<number | null> {
    const res = await this.pool.query<{ admin_id: number }>(
      'SELECT admin_id FROM support_conversations WHERE id = $1',
      [conversationId],
    )
    return res.rows[0]?.admin_id ?? null
  }

  async getSupportAgentIds(): Promise<number[]> {
    const res = await this.pool.query<{ id: number }>(
      `SELECT u.id FROM users u
       JOIN roles r ON u.role_id = r.id
       WHERE r.name = 'soporte'`,
    )
    return res.rows.map((r) => r.id)
  }
}
