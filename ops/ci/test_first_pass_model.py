import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'web/scripts/pipeline'))
from agents import SubscriptionAgent
from contracts import validate_contract

ROOT = Path(__file__).resolve().parents[2]


class Result:
    def __init__(self, stdout='', returncode=0):
        self.stdout, self.stderr, self.returncode = stdout, '', returncode


class FirstPassModelTests(unittest.TestCase):
    def agent(self, **extra):
        self.commands = []

        def runner(args, **kwargs):
            self.commands.append(args)
            if args[1] == 'login':
                return Result('Logged in using ChatGPT')
            output = args[args.index('--output-last-message') + 1]
            Path(output).write_text(json.dumps({'facts': [], 'noRelevantFacts': True, 'evidenceSha256': 'e', 'policySha256': 'p'}))
            return Result()
        config = {'provider': 'codex_subscription', 'allowApiBilling': False, 'maxCallsPerRun': 5,
                  'maxDocumentChars': 30000, 'timeoutSeconds': 5, **extra}
        return SubscriptionAgent(config, runner=runner)

    def model_of(self, command):
        return command[command.index('-m') + 1] if '-m' in command else None

    def test_without_the_setting_no_call_names_a_model(self):
        agent = self.agent()
        agent.extract('x' * 200, {'id': 'example'})
        self.assertIsNone(self.model_of(self.commands[-1]))

    def test_only_the_first_pass_uses_the_smaller_model(self):
        agent = self.agent(extractModel='gpt-6-luna')
        agent.extract('x' * 200, {'id': 'example'})
        self.assertEqual(self.model_of(self.commands[-1]), 'gpt-6-luna')
        agent.review_empty('x' * 200, {'id': 'example'}, {'body': {'sha256': 'e'}}, 'p')
        self.assertIsNone(self.model_of(self.commands[-1]))

    def test_contract_accepts_a_plain_model_name_and_refuses_anything_else(self):
        contract = json.loads((ROOT / 'contracts/market.json').read_text())
        self.assertNotIn('extractModel', contract['model'])
        validate_contract({**contract, 'model': {**contract['model'], 'extractModel': 'gpt-6-luna'}})
        for bad in ('', '--config', 'a b', 7):
            with self.assertRaises(ValueError):
                validate_contract({**contract, 'model': {**contract['model'], 'extractModel': bad}})


if __name__ == '__main__':
    unittest.main()
