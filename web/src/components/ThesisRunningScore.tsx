import { formatShortDate } from '../data/dates'
import { issues } from '../data/issues/index'
import { thesisRunningScore } from '../data/issueHelpers'

export function ThesisRunningScore() {
  const score = thesisRunningScore(issues)
  const text =
    score.total === 0
      ? 'No published issues yet.'
      : `Holds in ${score.holds} of ${score.total} issues since ${
          score.since ? formatShortDate(score.since) : ''
        }`

  return <p className="thesis-running-score">{text}</p>
}
