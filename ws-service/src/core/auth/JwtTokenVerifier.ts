import jwt from 'jsonwebtoken'
import type { TokenClaims, TokenVerifier } from './TokenVerifier'
import { UnauthorizedError } from '../errors'

/**
 * Verifica el JWT con el mismo SECRET_KEY/ALGORITHM que el backend Python.
 * Mapea los claims (sub, role, sid, circuit_id) al modelo del dominio.
 */
export class JwtTokenVerifier implements TokenVerifier {
  constructor(
    private readonly secret: string,
    private readonly algorithm: jwt.Algorithm = 'HS256',
  ) {}

  verify(token: string): TokenClaims {
    let payload: jwt.JwtPayload
    try {
      payload = jwt.verify(token, this.secret, { algorithms: [this.algorithm] }) as jwt.JwtPayload
    } catch {
      throw new UnauthorizedError('invalid token')
    }

    const sub = payload.sub
    if (sub === undefined || sub === null) throw new UnauthorizedError('no sub')

    return {
      userId:    Number(sub),
      role:      typeof payload.role === 'string' ? payload.role : '',
      sid:       typeof payload.sid === 'string' ? payload.sid : null,
      circuitId: payload.circuit_id != null ? Number(payload.circuit_id) : null,
    }
  }
}
