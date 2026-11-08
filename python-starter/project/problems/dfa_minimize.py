import re
from project.problem import Problem

class DFAMinimize(Problem):

    def initialize_parser(self, parser):
        parser.add_argument('--mini', action='store_true', help='Determinisztikus automata minimalizálása')

    def is_chosen_problem(self, args):
        return args.mini

    def run(self, args):
        self.minimize_dfa(args.input, args.output)

    def _get_state_num(self, state_name):
        match = re.search(r'\d+', state_name)
        return int(match.group()) if match else 0

    def minimize_dfa(self, input_file, output_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 4:
            print("Hibás vagy hiányos bemeneti fájl!")
            return

        original_states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2]
        final_states = set(lines[3].split())

        transitions = {s: {} for s in original_states}

        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                u, a, v = parts
                if u in original_states and v in original_states and a in alphabet:
                    transitions[u][a] = v

        states_list = original_states
        marked = set()
        pairs = []

        for i in range(len(states_list)):
            for j in range(i + 1, len(states_list)):
                p = states_list[i]
                q = states_list[j]
                pairs.append((p, q))
                
                if (p in final_states) != (q in final_states):
                    marked.add((p, q))
                    marked.add((q, p))

        changed = True
        while changed:
            changed = False
            for p, q in pairs:
                if (p, q) not in marked:
                    for a in alphabet:
                        p_next = transitions[p].get(a)
                        q_next = transitions[q].get(a)

                        if p_next and q_next and p_next != q_next:
                            if (p_next, q_next) in marked:
                                marked.add((p, q))
                                marked.add((q, p))
                                changed = True
                                break

        parent = {s: s for s in original_states}

        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j

        for p, q in pairs:
            if (p, q) not in marked:
                union(p, q)

        groups = {}
        for s in original_states:
            root = find(s)
            if root not in groups:
                groups[root] = []
            groups[root].append(s)

        state_mapping = {}
        for group in groups.values():
            smallest_state = min(group, key=self._get_state_num)
            new_name = 's' + str(self._get_state_num(smallest_state))
            for s in group:
                state_mapping[s] = new_name

        new_states = sorted(list(set(state_mapping.values())), key=self._get_state_num)
        new_start = state_mapping[start_state]
        
        new_final = set()
        for f in final_states:
            new_final.add(state_mapping[f])
        new_final_sorted = sorted(list(new_final), key=self._get_state_num)

        new_transitions = set()
        for u in original_states:
            for a, v in transitions[u].items():
                new_transitions.add((state_mapping[u], a, state_mapping[v]))

        sorted_new_transitions = sorted(list(new_transitions), key=lambda x: (
            self._get_state_num(x[0]), x[1], self._get_state_num(x[2])
        ))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(" ".join(new_states) + "\n")
            f.write(" ".join(alphabet) + "\n")
            f.write(new_start + "\n")
            f.write(" ".join(new_final_sorted) + "\n")
            for u, a, v in sorted_new_transitions:
                f.write(f"{u} {a} {v}\n")