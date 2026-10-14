import ts from 'typescript'
import { readFileSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const repo = resolve('..')
const base = process.env.SMP_BASE_SHA ?? 'HEAD'
const arrays: Record<string, string> = { 'web/src/data/tracker/suppliers.ts': 'manualTrackerSuppliers', 'web/src/data/tracker/events.ts': 'handCollectedEvents', 'web/src/data/evidence.ts': 'handWrittenEvidenceRecords' }
function literal(node: ts.Node): boolean {
  if (ts.isStringLiteral(node) || ts.isNumericLiteral(node) || [ts.SyntaxKind.TrueKeyword, ts.SyntaxKind.FalseKeyword, ts.SyntaxKind.NullKeyword].includes(node.kind)) return true
  if (ts.isPrefixUnaryExpression(node)) return [ts.SyntaxKind.MinusToken, ts.SyntaxKind.PlusToken].includes(node.operator) && ts.isNumericLiteral(node.operand)
  if (ts.isArrayLiteralExpression(node)) return node.elements.every(literal)
  if (ts.isObjectLiteralExpression(node)) return node.properties.every(p => ts.isPropertyAssignment(p) && (ts.isIdentifier(p.name) || ts.isStringLiteral(p.name)) && literal(p.initializer))
  return false
}
export function dataSurface(text: string, name: string): string {
  const file = ts.createSourceFile('data.ts', text, ts.ScriptTarget.Latest, true)
  let found: ts.ArrayLiteralExpression | undefined
  function visit(node: ts.Node) { if (ts.isVariableDeclaration(node) && node.name.getText(file) === name && node.initializer && ts.isArrayLiteralExpression(node.initializer)) found = node.initializer; ts.forEachChild(node, visit) }
  visit(file)
  if (!found || !literal(found)) throw new Error(`${name}: expected data literals only; code expression or missing array refused`)
  return text.slice(0, found.getStart(file)) + '[REVIEWED_DATA_ARRAY]' + text.slice(found.end)
}
export function verifyDataFile(before: string, after: string, name: string): void {
  if (dataSurface(before, name) !== dataSurface(after, name)) throw new Error('Collector changed code outside the allowed literal array')
}
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
 const changed = execFileSync('git', ['diff', '--name-only', base], { cwd: repo, encoding: 'utf8' }).trim().split('\n').filter(Boolean)
 for (const path of changed) {
  if (['web/src/data/generated/refreshVerification.json', 'web/src/data/generated/refreshPublication.json'].includes(path)) throw new Error(`Collector cannot certify its own refresh or advance public dates: ${path}`)
  if (path.startsWith('web/src/data/generated/') && path.endsWith('.json')) { JSON.parse(readFileSync(resolve(repo, path), 'utf8')); continue }
  if (!arrays[path]) throw new Error(`Unexpected collector change: ${path}`)
  const before = execFileSync('git', ['show', `${base}:${path}`], { cwd: repo, encoding: 'utf8' })
  const after = readFileSync(resolve(repo, path), 'utf8')
  verifyDataFile(before, after, arrays[path])
 }
 console.log(`Collector edit guard: ${changed.length} data paths checked; no code changes permitted.`)
}
