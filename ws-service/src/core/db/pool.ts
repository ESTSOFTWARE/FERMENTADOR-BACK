import { Pool } from 'pg'
import { config } from '../config/env'

/** Pool de PostgreSQL compartido (misma BD que el backend). */
export function createPool(): Pool {
  return new Pool({
    host:     config.db.host,
    port:     config.db.port,
    user:     config.db.user,
    password: config.db.password,
    database: config.db.database,
    max:      10,
    // SSL para BD gestionada (Supabase). El proveedor termina TLS; no verificamos CA.
    ssl:      config.db.ssl ? { rejectUnauthorized: false } : undefined,
  })
}
