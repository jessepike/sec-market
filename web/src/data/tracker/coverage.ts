export type FieldStatus = 'updated' | 'checked-no-change' | 'unavailable' | 'failed' | 'not-checked' | 'not-applicable' | 'configured'
export interface SourceCheck { url: string; checkedAt: string; status: 'ok' | 'failed'; sha256?: string; httpStatus?: number; reason?: string; finalUrl?: string }
export interface FieldCheck { supplierId: string; field: string; status: FieldStatus; checkedAt: string | null; sourceUrls: string[]; value: unknown; period?: string; reason: string; retained: boolean }
export interface SupplierCheck { supplierId: string; checkedAt: string; sourceChecks: SourceCheck[]; fields: Array<{ field: string; status: FieldStatus; sourceUrls: string[]; discoverySourceUrls?: string[]; reason: string }> }
export interface RefreshCoverage {
  checkedAt: string
  state: 'complete' | 'incomplete'
  allSuppliersAttempted: boolean
  supplierCount: number
  supplierChecksReceived: number
  sourceChecks: SourceCheck[]
  fields: FieldCheck[]
  summary: Record<FieldStatus, number>
  schedule: { enabled: boolean; timezone: string; time: string; blocker: string | null }
}

/** A fetched historical document alone is not proof that no newer disclosure exists. */
export function supportedFieldStatus(field: SupplierCheck['fields'][number] | undefined, sources: SourceCheck[]): FieldStatus {
  if (!field) return 'not-checked'
  if (!['updated', 'checked-no-change', 'unavailable', 'failed', 'not-applicable'].includes(field.status)) return 'not-checked'
  if (['updated', 'checked-no-change', 'unavailable'].includes(field.status)) {
    const proven = field.sourceUrls.some(url => sources.some(s => s.url === url && s.status === 'ok' && /^[a-f0-9]{64}$/.test(s.sha256 ?? '') && Number.isFinite(Date.parse(s.checkedAt))))
    return proven ? field.status : 'not-checked'
  }
  return field.status
}

export const requiredFieldGroups = ['identity', 'headlineMetric', 'lastRound', 'ownership', 'revenue.latest', 'revenue.prior', 'events'] as const
export function checkedSource(url: string, sources: SourceCheck[]): boolean {
  return sources.some(s => s.url === url && s.status === 'ok' && /^[a-f0-9]{64}$/.test(s.sha256 ?? '') && Number.isFinite(Date.parse(s.checkedAt)))
}
export function verifyClaimSources(field: SupplierCheck['fields'][number] | undefined, sources: SourceCheck[], supportingUrls: string[]): string | null {
  if (!field || !['updated', 'checked-no-change', 'unavailable'].includes(field.status)) return null
  if (!(field.discoverySourceUrls ?? []).some(url => checkedSource(url, sources))) return 'No hashed current company or parent discovery check; retained claim is not verified current.'
  if (supportingUrls.length && !supportingUrls.some(url => field.sourceUrls.includes(url) && checkedSource(url, sources))) return 'The primary document supporting the displayed claim was not checked in this field receipt.'
  return null
}
export function validateSupplierChecks(checks: SupplierCheck[], supplierIds: string[], now = Date.now()): void {
  const seen = new Set<string>()
  for (const check of checks) {
    if (!supplierIds.includes(check.supplierId) || seen.has(check.supplierId)) throw new Error(`Unexpected or duplicated supplier receipt: ${check.supplierId}`)
    seen.add(check.supplierId)
    const at = Date.parse(check.checkedAt)
    if (!Number.isFinite(at) || at > now + 300000 || now - at > 36 * 3600000) throw new Error(`${check.supplierId}: invalid or stale check date`)
    if (!Array.isArray(check.sourceChecks) || !Array.isArray(check.fields)) throw new Error(`${check.supplierId}: missing source or field checks`)
    const groups = check.fields.map(f => f.field)
    if (groups.length !== requiredFieldGroups.length || requiredFieldGroups.some(f => !groups.includes(f))) throw new Error(`${check.supplierId}: expected each of the seven field groups exactly once`)
    for (const source of check.sourceChecks) {
      if (!/^https?:\/\//.test(source.url) || !['ok', 'failed'].includes(source.status)) throw new Error(`${check.supplierId}: invalid source check`)
      const sourceAt = Date.parse(source.checkedAt)
      if (!Number.isFinite(sourceAt) || sourceAt > now + 300000 || now - sourceAt > 36 * 3600000) throw new Error(`${check.supplierId}: source check has invalid or stale date`)
    }
  }
}
