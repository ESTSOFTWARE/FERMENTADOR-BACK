import type { ChannelDescriptor } from '../../../core/ws/ChannelDescriptor'

/** /ws/notifications/{userId} — notificaciones en tiempo real. */
export const notificationsChannel: ChannelDescriptor = {
  channel: 'notifications',
  path:    'notifications',
}
