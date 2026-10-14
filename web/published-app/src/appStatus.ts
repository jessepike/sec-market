import raw from './release-status.json' with { type: 'json' }
export const status = raw as { lastCompleteRefreshAt: string | null; lastAttemptAt: string; appRevision: string | null; suppliersAttempted: number; supplierCount: number; failedSupplierIds: string[] }

export const format = (date: string | null) => date ? new Date(date).toLocaleString('en-GB', { timeZone: 'UTC', dateStyle: 'medium', timeStyle: 'short' }) + ' UTC' : 'not established'
export const completeRefreshLabel = format(status.lastCompleteRefreshAt)

