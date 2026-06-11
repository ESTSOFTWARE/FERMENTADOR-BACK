/** Datos que el typing del chat necesita consultar (membresía + nombre). */
export interface ChatTypingRepository {
  isMember(conversationId: number, userId: number): Promise<boolean>
  getMemberIds(conversationId: number): Promise<number[]>
  getUserName(userId: number): Promise<string>
}
