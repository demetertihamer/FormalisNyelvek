import argparse
import sys
from collections import deque
from project.problem import Problem

class DeterminizeProblem(Problem):
    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--det',action='store_true',help='Determinizalja a megadtt automatat')

    def is_chosen_problem(self, args):
        return getattr(args,'det',False)

    def run(self, args):
        with open(args.input,'r',encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        raw_states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2].strip()
        final_states = set(lines[3].split())

        states_set=set(raw_states)
        alphabet_set=set(alphabet)

        if start_state not in states_set:
            sys.exit(f"Hiba: A kezdőállapot '{start_state}' nincs az állapotok között.")

        for fs in final_states:
            if fs not in states_set:
                sys.exit(f"Hiba: A végállapot ({fs}) nem szerepel az állapotok között!")

        nfa_transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                src, symbol, dst = parts
                if src not in states_set or dst not in states_set:
                    sys.exit(f"Hiba: Ismeretlen állapot az átmenetben: {line}")
                if symbol not in alphabet_set:
                    sys.exit(f"Hiba: Ismeretlen bemeneti jel az átmenetben: {line}")

                if (src, symbol) not in nfa_transitions:
                    nfa_transitions[(src, symbol)] = set()
                nfa_transitions[(src, symbol)].add(dst)

        initial_subset = frozenset([start_state])

        subset_to_name = {initial_subset: 's0'}
        name_to_subset = {'s0': initial_subset}
        queue = deque([initial_subset])
        counter = 1

        dfa_transitions = []

        while queue:
            current_subset = queue.popleft()
            current_name = subset_to_name[current_subset]

            for symbol in alphabet:
                next_subset_builder=set()
                for state in current_subset:
                    if (state, symbol) in nfa_transitions:
                        next_subset_builder.update(nfa_transitions[(state,symbol)])

                if next_subset_builder:
                    next_subset=frozenset(next_subset_builder)
                    if next_subset not in subset_to_name:
                        new_name=f's{counter}'
                        counter+=1
                        subset_to_name[next_subset]=new_name
                        name_to_subset[new_name]=next_subset
                        queue.append(next_subset)

                    dst_name = subset_to_name[next_subset]
                    dfa_transitions.append((current_name,symbol,dst_name))

        ordered_state_names = [f"s{i}" for i in range(len(subset_to_name))] 

        dfa_final_states = [
            name for name in ordered_state_names
            if any (s in final_states for s in name_to_subset[name])
        ]

        def sort_key(transition):
            src,symbol,dst=transition
            src_index=int(src[1:])
            dst_index=int(dst[1:])
            return (src_index, symbol, dst_index)

        dfa_transitions.sort(key=sort_key)

        output_lines = [
            ' '.join(ordered_state_names),
            ' '.join(alphabet),
            's0',
            ' '.join(dfa_final_states)
        ]

        for src, symbol, dst in dfa_transitions:
            output_lines.append(f"{src} {symbol} {dst}")

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines) + '\n')