import { evidenceById } from './evidence'
import type { TrackedClaim, VendorPrint } from './types'

/** Parse a comparable growth print such as +21% or 12%. Null if the value is not a rate. */
export function growthPoints(value: string): number | null {
  const trimmed = value.trim()
  if (!trimmed.endsWith('%')) return null
  const n = Number(trimmed.slice(0, -1).replace('+', ''))
  return Number.isFinite(n) ? n : null
}

export function renderMetricPrint(print: VendorPrint): string {
  return [print.metric, print.value].filter(Boolean).join(' ')
}

export function renderClosePrint(actor: string, value: string, isoDate: string): string {
  const date = new Date(`${isoDate}T00:00:00Z`)
  const month = date.toLocaleString('en-US', { month: 'short', timeZone: 'UTC' })
  const year = String(date.getUTCFullYear())
  return [actor, value, `closed ${month} ${year}`].join(' · ')
}

export function trackedFrom(ids: string[]): TrackedClaim {
  const [first, ...rest] = ids
  if (!first) {
    throw new Error('TrackedClaim requires at least one evidence id')
  }
  const observedOn = evidenceById[first]?.publicationDate
  if (!observedOn) {
    throw new Error(`TrackedClaim evidence ${first} is missing a publicationDate`)
  }
  return { layer: 'tracked', evidenceIds: [first, ...rest], observedOn }
}

export function isCurrentPrint(print: VendorPrint): boolean {
  return print.surface !== 'coverage'
}

export function groupPositionKey(group: string, position: string): string {
  return group + ':' + position
}

export function fasterPeerRead(peers: VendorPrint[]): string {
  return (
    peers.map((peer) => peer.name + ' at ' + peer.value).join(' and ') +
    ' are printing faster in the same category.'
  )
}

export function infraCarriedRead(value: string): string {
  return 'Networking orders ' + value + ' carried the quarter. Security did not.'
}

export function identityAbsorbedRead(actor: string): string {
  return 'Identity becomes a ' + actor + ' platform pillar. Capital, not customer spend.'
}

export function identityHoldingRead(name: string, momentum: string): string {
  return 'IGA is up while the ' + name + ' domain overall is ' + momentum.replace(/-/g, ' ') + '.'
}

export function fasterThanOrganicRead(name: string): string {
  return 'Growing faster than ' + name + ' organic. A split inside the category, not a new SASE wave.'
}
