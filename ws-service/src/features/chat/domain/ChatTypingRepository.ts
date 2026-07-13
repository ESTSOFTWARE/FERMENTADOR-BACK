/** Datos que el typing y la presencia del chat necesitan consultar. */
export interface ChatTypingRepository {
  isMember(conversationId: number, userId: number): Promise<boolean>
  getMemberIds(conversationId: number): Promise<number[]>
  getUserName(userId: number): Promise<string>
  getChatableUserIds(userId: number): Promise<Set<number>>
}
