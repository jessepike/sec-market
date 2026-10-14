import publication from './generated/refreshPublication.json' with { type: 'json' }
export const lastCompleteRefreshAt = publication.lastCompleteRefreshAt as string | null
export const lastAttemptAt = publication.lastAttemptAt
export const completeRefreshDisplay = lastCompleteRefreshAt
  ? new Date(lastCompleteRefreshAt).toISOString().replace('T', ' ').replace('.000Z', ' UTC')
  : 'not established'
export const appDeployment = publication.appDeployment
