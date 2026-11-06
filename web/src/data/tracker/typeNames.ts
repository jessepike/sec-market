/** Display name for an event type: "Leadership", "Layoffs", "SEC filing". */
export const typeName = (type: string): string => ({ 'exec-change': 'Leadership', 'going-concern': 'Going concern', layoff: 'Layoffs', filing: 'SEC filing', 'late-filing': 'Late filing' } as Record<string, string>)[type] ?? type.replaceAll('-', ' ')
