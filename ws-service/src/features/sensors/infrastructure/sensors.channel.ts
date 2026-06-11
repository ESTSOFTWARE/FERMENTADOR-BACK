import type { ChannelDescriptor } from '../../../core/ws/ChannelDescriptor'

/** /ws/sensors/{circuitId} — datos de sensores; cada socket entra a la sala del circuito. */
export const sensorsChannel: ChannelDescriptor = {
  channel: 'sensors',
  path:    'sensors',
  roomFromParams: (params) => (params[0] ? `circuit:${params[0]}` : null),
}
