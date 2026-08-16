export const REPO_BLOB_BASE = 'https://github.com/jessepike/sec-market/blob/main'

const ARTIFACT_PATHS: Record<string, string> = {
  'SEC-MARKET-SIG-SRC-002': '/docs/active/market-signal-episode-002-source-manifest.md',
  'SEC-MARKET-SIG-EV-002': '/docs/active/market-signal-episode-002-evidence.md',
  'SEC-MARKET-SIG-BL-002': '/docs/active/market-signal-episode-002-baseline.md',
  'SEC-MARKET-SIG-PANEL-002': '/docs/active/market-signal-episode-002-panel.md',
  'SEC-MARKET-SIG-002': '/docs/active/market-signal-episode-002-brief.md',
}

export function researchArtifactUrl(artifactLabel: string): string | null {
  for (const [prefix, path] of Object.entries(ARTIFACT_PATHS)) {
    if (artifactLabel.startsWith(prefix)) {
      return `${REPO_BLOB_BASE}${path}`
    }
  }
  return null
}
