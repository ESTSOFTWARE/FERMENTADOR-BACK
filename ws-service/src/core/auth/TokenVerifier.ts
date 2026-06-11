export interface TokenClaims {
  userId:    number
  role:      string
  sid:       string | null
  circuitId: number | null
}

/** Verifica el JWT de la cookie (mismo SECRET_KEY que el backend). */
export interface TokenVerifier {
  /** Devuelve los claims o lanza un error si el token es inválido/expirado. */
  verify(token: string): TokenClaims
}
