import argparse
from project.problem import Problem

class DFAProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--check', help='word or comma-separated words to check', type=str)

    def is_chosen_problem(self, args):
        return args.check is not None

    def run(self, args):
        with open(args.input, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2].strip()
        final_states = set(lines[3].split())

        transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                src, symbol, dst = parts
                transitions[(src, symbol)] = dst

        words_to_check = [w.strip() for w in args.check.split(',')]

        results = []
        for word in words_to_check:
            current_state = start_state
            accepted = True

            for ch in word:
                if (current_state, ch) in transitions:
                    current_state = transitions[(current_state, ch)]
                else:
                    accepted = False
                    break

            if accepted and current_state in final_states:
                results.append("IGEN")
            else:
                results.append("NEM")

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('\n'.join(results) + '\n')