import http from 'node:http'
import { WebSocketServer, WebSocket } from 'ws'
import type { Connection } from './Connection'
import type { ChannelDescriptor } from './ChannelDescriptor'
import type { ConnectionRegistry } from './ConnectionRegistry'
import type { HandleConnection } from './HandleConnection'
import type { HandleDisconnect } from './HandleDisconnect'
import { UnauthorizedError } from '../errors'

function parseCookie(header: string | undefined, name: string): string | undefined {
  if (!header) return undefined
  for (const part of header.split(';')) {
    const [k, ...v] = part.trim().split('=')
    if (k === name) return decodeURIComponent(v.join('='))
  }
  return undefined
}

/**
 * Servidor WebSocket genérico. No conoce ningún canal en concreto: recibe los
 * ChannelDescriptor que exporta cada feature y enruta según el path.
 */
export class SocketServer {
  private readonly httpServer: http.Server
  private readonly wss: WebSocketServer
  private readonly byPath = new Map<string, ChannelDescriptor>()

  constructor(
    private readonly registry: ConnectionRegistry,
    private readonly handleConnection: HandleConnection,
    private readonly handleDisconnect: HandleDisconnect,
    descriptors: ChannelDescriptor[],
  ) {
    for (const d of descriptors) this.byPath.set(d.path, d)

    this.httpServer = http.createServer((req, res) => {
      if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify({ status: 'ok', connections: this.registry.size() }))
        return
      }
      res.writeHead(404); res.end()
    })
    this.wss = new WebSocketServer({ server: this.httpServer })
    this.wss.on('connection', (socket, req) => void this.onConnection(socket, req))
  }

  private async onConnection(socket: WebSocket, req: http.IncomingMessage): Promise<void> {
    const url   = new URL(req.url ?? '', 'http://localhost')
    const parts = url.pathname.split('/').filter(Boolean) // ["ws","sensors","12"]
    if (parts[0] !== 'ws' || !parts[1]) { socket.close(4404); return }

    const descriptor = this.byPath.get(parts[1])
    if (!descriptor) { socket.close(4404); return }

    const token =
      url.searchParams.get('token') ??
      parseCookie(req.headers.cookie, 'access_token')

    let conn: Connection
    try {
      conn = await this.handleConnection.execute(token, descriptor.channel, socket)
    } catch (err) {
      socket.close(err instanceof UnauthorizedError ? 4401 : 1011)
      return
    }

    const room = descriptor.roomFromParams?.(parts.slice(2))
    if (room) this.registry.joinRoom(conn, room)

    const ctx = { registry: this.registry }

    if (descriptor.onConnect) {
      Promise.resolve(descriptor.onConnect(conn, ctx)).catch(() => { /* ignore */ })
    }

    socket.on('message', (raw) => {
      if (!descriptor.onClientMessage) return
      let data: Record<string, unknown>
      try { data = JSON.parse(raw.toString()) } catch { return }
      Promise.resolve(descriptor.onClientMessage(conn, data)).catch(() => { /* ignore */ })
    })

    let disconnected = false
    const doDisconnect = () => {
      if (disconnected) return
      disconnected = true
      this.handleDisconnect.execute(conn)
      if (descriptor.onDisconnect) {
        Promise.resolve(descriptor.onDisconnect(conn, ctx)).catch(() => { /* ignore */ })
      }
    }
    socket.on('close', doDisconnect)
    socket.on('error', doDisconnect)
  }

  listen(port: number): void {
    this.httpServer.listen(port, () => console.info(`[WS] escuchando en :${port}`))
  }
}
