import type { ChannelDescriptor } from '../../../core/ws/ChannelDescriptor'

/** /ws/session — expulsión instantánea de sesión (session:revoked). */
export const sessionChannel: ChannelDescriptor = {
  channel: 'session',
  path:    'session',
}
