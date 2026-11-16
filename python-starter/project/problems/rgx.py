import re
from collections import Counter
from project.problem import Problem

# Pontosan a feladatleírásban megadott minta, ^ és $ nélkül[cite: 4]
LOGCAT_PATTERN = re.compile(
    r"(([0-9-]+) ([0-9:.]+)) +([0-9]+) +([0-9]+) ([IDVEFAW]) (.+?):(?: (.+))?"
)


class RegexProblem(Problem):

    def initialize_parser(self, parser):
        parser.add_argument("--rgx", type=int, help="Regex feladat sorszama (1-5)")

    def is_chosen_problem(self, args):
        return args.rgx is not None

    def run(self, args):
        with open(args.input, "r", encoding="utf-8-sig", errors="replace") as f:
            lines = f.read().splitlines()

        if args.rgx == 1:
            results = self.task_1(lines)
        elif args.rgx == 2:
            results = self.task_2(lines)
        elif args.rgx == 3:
            results = self.task_3(lines)
        elif args.rgx == 4:
            results = self.task_4(lines)
        elif args.rgx == 5:
            results = self.task_5(lines)
        else:
            results = []

        with open(args.output, "w", encoding="utf-8") as f:
            for line in results:
                f.write(f"{line}\n")

    def task_1(self, lines: list[str]) -> list[str]:
        patterns = [
            # 1. az összes sort, amelyik 10. hónap 15-én jött létre[cite: 2]
            re.compile(r"10-15 [0-9:.]+ +[0-9]+ +[0-9]+ [IDVEFAW] "),
            # 2. az összes sort, amelyik 10. hónap 15-én 10 óra 18 perc és 51 másodperckor jött létre[cite: 2]
            re.compile(r"10-15 10:18:51\.[0-9]+ +[0-9]+ +[0-9]+ [IDVEFAW] "),
            # 3. az összes sort, amelyik 51 másodperckor jött létre (mindegy a perc)[cite: 2]
            re.compile(r"[0-9-]+ [0-9]{2}:[0-9]{2}:51\.[0-9]+ +[0-9]+ +[0-9]+ [IDVEFAW] "),
            # 4. az összes lowmemorykiller taget tartalmazó sor[cite: 2]
            re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [IDVEFAW] [^:]*lowmemorykiller[^:]*:"),
            # 5. az összes 10:18:51 kor keletkező 221-es process id-jú sort[cite: 2]
            re.compile(r"[0-9-]+ 10:18:51\.[0-9]+ +221 +[0-9]+ [IDVEFAW] "),
            # 6. az összes hibát tartalmazó sort (E)[cite: 3]
            re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ E "),
            # 7. az összes warningot (W) amit a PackageManager küld[cite: 3]
            re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ W [^:]*PackageManager[^:]*:"),
            # 8. az összes ExoPlayer-es debug (D) infót[cite: 3]
            re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ D [^:]*ExoPlayer[^:]*:"),
            # 9. az összes java állomány pozíciót tartalmazó hibát és warningot (EW .java:)[cite: 3]
            re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [EW] .+\.java:"),
            # 10. az összes olyan sort, ami tartalmazza a Thread szót a message részben (nem a tagben)[cite: 3]
            re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [IDVEFAW] (?:(?!Thread)[^:])+:.*Thread"),
        ]

        return [str(sum(1 for line in lines if pat.search(line))) for pat in patterns]

    def task_2(self, lines: list[str]) -> list[str]:
        java_file_pattern = re.compile(r"\(([A-Za-z0-9_$]+\.java):[0-9]+\)")
        extracted_files = []
        in_error_block = False

        for line in lines:
            match = LOGCAT_PATTERN.search(line)
            if match:
                in_error_block = (match.group(6) == "E")

            if in_error_block:
                for file_match in java_file_pattern.finditer(line):
                    extracted_files.append(file_match.group(1))

        return extracted_files

    def task_3(self, lines: list[str]) -> list[str]:
        seen_pids = set()
        ordered_pids = []

        for line in lines:
            match = LOGCAT_PATTERN.search(line)
            if match:
                pid = match.group(4)
                if pid not in seen_pids:
                    seen_pids.add(pid)
                    ordered_pids.append(pid)

        return ordered_pids

    def task_4(self, lines: list[str]) -> list[str]:
        error_counts = Counter()

        for line in lines:
            match = LOGCAT_PATTERN.search(line)
            if match and match.group(6) == "E":
                error_counts[match.group(4)] += 1

        if not error_counts:
            return []

        top_pid, max_errors = error_counts.most_common(1)[0]
        return [f"PID={top_pid} ({max_errors} errors)"]

    def task_5(self, lines: list[str]) -> list[str]:
        main_thread_errors = 0

        for line in lines:
            match = LOGCAT_PATTERN.search(line)
            if match and match.group(6) == "E":
                if match.group(4) == match.group(5):
                    main_thread_errors += 1

        return [str(main_thread_errors)]