import { config } from '../lib/core.js'
import { handle } from '../lib/requests.js'

// Public endpoint for the "Want a company tracked?" box on the site.
const run = request => handle(request, config(process.env))
export const POST = run
export const OPTIONS = run
