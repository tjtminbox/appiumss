import { getAssetFromKV } from '@cloudflare/kv-asset-handler'

addEventListener('fetch', event => {
  event.respondWith(handleEvent(event))
})

async function handleEvent(event) {
  try {
    // Try to get the static asset from KV
    return await getAssetFromKV(event)
  } catch (e) {
    // If the static asset is not found, forward to your Flask app
    return fetch(`${FLASK_URL}${new URL(event.request.url).pathname}`, event.request)
  }
}
