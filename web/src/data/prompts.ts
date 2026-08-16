import type { ConversationPrompt } from './types'

export const conversationPrompts: ConversationPrompt[] = [
  {
    id: 'prompt-activation',
    audience: 'Account lead / CSP',
    prompt:
      'When cloud or AI capacity becomes operational, what applications, sensitive data, and machine identities go live — and on what timeline?',
    whenToUse:
      'Next account plan, QBR, or client discussion involving cloud/AI capacity. Stop at INVESTIGATE if no relevant activation exists.',
    evidenceIds: ['LAG-NO-CALL', 'A1b', 'D3'],
  },
  {
    id: 'prompt-cloud',
    audience: 'Security practice lead',
    prompt:
      'For this workload: what do native cloud controls already cover, and what residual gaps remain unknown?',
    whenToUse: 'Step 1 identifies relevant cloud or AI capacity activation.',
    evidenceIds: ['D5a', 'D7'],
  },
  {
    id: 'prompt-identity',
    audience: 'Security practice lead',
    prompt:
      'Who and what acts in this environment — including non-human identities with delegated access?',
    whenToUse: 'Accounts introducing consequential machine identities or production AI.',
    evidenceIds: ['C7', 'D7', 'D5b'],
  },
  {
    id: 'prompt-data',
    audience: 'Security practice lead',
    prompt:
      'What sensitive data enters the workload, and what governance or protection gaps would block safe scaling?',
    whenToUse: 'Sensitive-data or production AI activation on the account.',
    evidenceIds: ['C8a', 'C8b', 'D2'],
  },
  {
    id: 'prompt-network',
    audience: 'Network / SASE owner',
    prompt:
      'Is firewall refresh or SASE displacement already underway — and is momentum tied to lifecycle evidence, not assumed infrastructure lag?',
    whenToUse: 'Refresh or displacement already exists on the account.',
    evidenceIds: ['C3', 'C4', 'C6'],
  },
  {
    id: 'prompt-no-boom',
    audience: 'Any GTM or client conversation',
    prompt:
      'We are not claiming a measured market-wide cybersecurity boom or a stable infrastructure-to-security lag. What specific exposure does this account have?',
    whenToUse: 'Before scaling messaging or implying category-wide spend acceleration.',
    evidenceIds: ['LAG-NO-CALL', 'D1'],
  },
  {
    id: 'prompt-budget',
    audience: 'Client executive',
    prompt:
      'Security budgets grew 4% in 2025 while security\'s share of IT fell to 10.9%. Where is incremental investment going — AI infrastructure, cloud, or security — and what tradeoffs are you making?',
    whenToUse: 'Budget planning or investment prioritization conversations.',
    evidenceIds: ['D1', 'D2'],
  },
]
