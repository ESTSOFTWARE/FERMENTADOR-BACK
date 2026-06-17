import 'dotenv/config'

function required(name: string): string {
  const value = process.env[name]
  if (!value) throw new Error(`Falta la variable de entorno ${name}`)
  return value
}

export const config = {
  port: Number(process.env.PORT ?? 8003),

  jwt: {
    secret:    required('JWT_SECRET'),
    algorithm: (process.env.JWT_ALGORITHM ?? 'HS256') as 'HS256',
  },

  db: {
    host:     process.env.DB_HOST ?? 'localhost',
    port:     Number(process.env.DB_PORT ?? 5432),
    user:     required('DB_USER'),
    password: required('DB_PASSWORD'),
    database: required('DB_NAME'),
    ssl:      process.env.DB_SSL === 'true',   // true para BD gestionada (Supabase)
  },

  rabbitmq: {
    url:      process.env.RABBITMQ_URL ?? 'amqp://guest:guest@localhost:5672',
    exchange: process.env.WS_EXCHANGE ?? 'ws.events',
  },
}
