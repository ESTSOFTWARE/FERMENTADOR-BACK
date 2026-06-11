/** Lee la sesión activa de un usuario para validar la sesión única (sid). */
export interface SessionRepository {
  getActiveSessionId(userId: number): Promise<string | null>
}
