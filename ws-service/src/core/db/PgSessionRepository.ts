import type { Pool } from 'pg'
import type { SessionRepository } from './SessionRepository'

/** Lee users.active_session_id de PostgreSQL (misma BD que el backend). */
export class PgSessionRepository implements SessionRepository {
  constructor(private readonly pool: Pool) {}

  async getActiveSessionId(userId: number): Promise<string | null> {
    const res = await this.pool.query<{ active_session_id: string | null }>(
      'SELECT active_session_id FROM users WHERE id = $1',
      [userId],
    )
    return res.rows[0]?.active_session_id ?? null
  }
}
