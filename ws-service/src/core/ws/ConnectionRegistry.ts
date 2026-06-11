import type { Connection } from './Connection'

/**
 * Registro de conexiones activas. Permite encontrar a quién entregar un evento,
 * tanto por usuario como por sala (rooms para sensores / typing).
 */
export interface ConnectionRegistry {
  add(conn: Connection): void
  remove(conn: Connection): void

  getByUser(userId: number): Connection[]

  // Salas (sensores: circuit:{id} | typing: conv:{id})
  joinRoom(conn: Connection, room: string): void
  getByRoom(room: string): Connection[]

  size(): number
}
