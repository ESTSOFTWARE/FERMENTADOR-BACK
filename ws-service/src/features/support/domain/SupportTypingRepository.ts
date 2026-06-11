/** Datos que el typing de soporte necesita: admin dueño + agentes de soporte. */
export interface SupportTypingRepository {
  getAdminId(conversationId: number): Promise<number | null>
  getSupportAgentIds(): Promise<number[]>
}
