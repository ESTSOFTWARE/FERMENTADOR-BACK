import type { Connection } from './Connection'
import type { ConnectionRegistry } from './ConnectionRegistry'

/**
 * Registro en memoria por instancia. En multi-instancia, cada Node tiene el
 * suyo y entrega a SUS sockets locales (RabbitMQ reparte el evento a todas).
 */
export class InMemoryConnectionRegistry implements ConnectionRegistry {
  private readonly byUser = new Map<number, Set<Connection>>()
  private readonly byRoom = new Map<string, Set<Connection>>()
  private readonly rooms  = new Map<string, Set<string>>() // connId → rooms

  add(conn: Connection): void {
    let set = this.byUser.get(conn.userId)
    if (!set) { set = new Set(); this.byUser.set(conn.userId, set) }
    set.add(conn)
  }

  remove(conn: Connection): void {
    const set = this.byUser.get(conn.userId)
    if (set) {
      set.delete(conn)
      if (set.size === 0) this.byUser.delete(conn.userId)
    }
    const myRooms = this.rooms.get(conn.id)
    if (myRooms) {
      for (const room of myRooms) {
        const rset = this.byRoom.get(room)
        if (rset) {
          rset.delete(conn)
          if (rset.size === 0) this.byRoom.delete(room)
        }
      }
      this.rooms.delete(conn.id)
    }
  }

  getByUser(userId: number): Connection[] {
    return Array.from(this.byUser.get(userId) ?? [])
  }

  joinRoom(conn: Connection, room: string): void {
    let rset = this.byRoom.get(room)
    if (!rset) { rset = new Set(); this.byRoom.set(room, rset) }
    rset.add(conn)

    let myRooms = this.rooms.get(conn.id)
    if (!myRooms) { myRooms = new Set(); this.rooms.set(conn.id, myRooms) }
    myRooms.add(room)
  }

  getByRoom(room: string): Connection[] {
    return Array.from(this.byRoom.get(room) ?? [])
  }

  size(): number {
    let total = 0
    for (const set of this.byUser.values()) total += set.size
    return total
  }
}
