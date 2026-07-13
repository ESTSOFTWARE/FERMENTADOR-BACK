import type { Pool } from 'pg'
import type { ChatTypingRepository } from '../domain/ChatTypingRepository'

/** Consulta membresía del chat, nombre y contactos del usuario en PostgreSQL. */
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

  async getChatableUserIds(userId: number): Promise<Set<number>> {
    // 1. Obtener rol y created_by del usuario
    const userRes = await this.pool.query<{ created_by: number | null; role: string }>(
      `SELECT u.created_by, r.name AS role
       FROM users u
       JOIN roles r ON u.role_id = r.id
       WHERE u.id = $1`,
      [userId],
    )
    const user = userRes.rows[0]
    if (!user) return new Set()

    const { role, created_by } = user

    // soporte: solo puede ver a admins
    if (role === 'soporte') {
      const res = await this.pool.query<{ id: number }>(
        `SELECT u.id FROM users u JOIN roles r ON u.role_id = r.id WHERE r.name = 'admin'`,
      )
      const ids = new Set(res.rows.map((r) => r.id))
      ids.delete(userId)
      return ids
    }

    // Determinar admin_id
    let adminId: number | null = null
    if (role === 'admin') {
      adminId = userId
    } else if (role === 'profesor' || role === 'estudiante') {
      adminId = await this._findAdminId(created_by)
    } else {
      return new Set()
    }

    if (adminId === null) return new Set()

    // Usuarios directamente creados por el admin (profesores, etc.) sin soporte
    const profRes = await this.pool.query<{ id: number }>(
      `SELECT u.id FROM users u JOIN roles r ON u.role_id = r.id
       WHERE u.created_by = $1 AND r.name != 'soporte'`,
      [adminId],
    )
    const profIds = profRes.rows.map((r) => r.id)

    // Estudiantes de esos profesores sin soporte
    let studentIds: number[] = []
    if (profIds.length > 0) {
      const studRes = await this.pool.query<{ id: number }>(
        `SELECT u.id FROM users u JOIN roles r ON u.role_id = r.id
         WHERE u.created_by = ANY($1) AND r.name != 'soporte'`,
        [profIds],
      )
      studentIds = studRes.rows.map((r) => r.id)
    }

    const all = new Set<number>([adminId, ...profIds, ...studentIds])
    all.delete(userId)
    return all
  }

  private async _findAdminId(startId: number | null): Promise<number | null> {
    let currentId = startId
    for (let i = 0; i < 5; i++) {
      if (currentId === null) return null
      const res = await this.pool.query<{ created_by: number | null; role: string }>(
        `SELECT u.created_by, r.name AS role
         FROM users u JOIN roles r ON u.role_id = r.id
         WHERE u.id = $1`,
        [currentId],
      )
      const row = res.rows[0]
      if (!row) return null
      if (row.role === 'admin') return currentId
      currentId = row.created_by
    }
    return null
  }
}
