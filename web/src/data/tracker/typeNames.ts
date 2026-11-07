/** Display name for an event type, the same everywhere a reader sees it: "Acquisition", "Leadership change". */
const NAMES: Record<string, string> = {
  acquisition: 'Acquisition',
  divestiture: 'Divestiture',
  funding: 'Funding round',
  results: 'Results',
  restructuring: 'Restructuring',
  layoff: 'Layoffs',
  shutdown: 'Shutdown',
  'going-concern': 'Going concern',
  'late-filing': 'Late filing',
  debt: 'Debt',
  rating: 'Credit rating',
  'exec-change': 'Leadership change',
  filing: 'SEC filing',
}
export const typeName = (type: string): string => NAMES[type] ?? type.charAt(0).toUpperCase() + type.slice(1).replaceAll('-', ' ')
