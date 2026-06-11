import { createApp } from './app'

async function main(): Promise<void> {
  const app = createApp()
  await app.start()

  const shutdown = async () => {
    console.info('[WS] cerrando...')
    await app.stop()
    process.exit(0)
  }
  process.on('SIGINT', shutdown)
  process.on('SIGTERM', shutdown)
}

main().catch((err) => {
  console.error('[WS] fallo al iniciar:', err)
  process.exit(1)
})
