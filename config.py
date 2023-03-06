BASE_CORE_BRANCH_NAME = None
HEAD_CORE_BRANCH_NAME = None

BASE_RULE_BRANCH_NAME = None
HEAD_RULE_BRANCH_NAME = None

BASE_BRANCH_FILE_NAME = None
HEAD_BRANCH_FILE_NAME = None

SLACK_SUMMARY_FILE_NAME = "slack_summary.txt"
OUTPUT_FILE_NAME = "output.xlsx"
PRIVADO_CORE_URL = "https://github.com/Privado-Inc/privado-core"
PRIVADO_URL = "https://github.com/Privado-Inc/privado"


def init(args):
    global BASE_CORE_BRANCH_NAME, HEAD_CORE_BRANCH_NAME, BASE_RULE_BRANCH_NAME, HEAD_RULE_BRANCH_NAME

    if args.use_rule_compare:
        core_branch_names = get_core_branch(args.base, args.head, args.rules_branch_base,
                                            args.rules_branch_head)
        BASE_CORE_BRANCH_NAME = core_branch_names[0]
        HEAD_CORE_BRANCH_NAME = core_branch_names[1]
    else:
        BASE_CORE_BRANCH_NAME = args.base
        HEAD_CORE_BRANCH_NAME = args.head

    rule_branch_name = get_rules_branch(BASE_CORE_BRANCH_NAME, HEAD_CORE_BRANCH_NAME, args.rules_branch_base,
                                        args.rules_branch_head)

    BASE_RULE_BRANCH_NAME = rule_branch_name[0]
    HEAD_RULE_BRANCH_NAME = rule_branch_name[1]

    resolve_core_branch_file_name(BASE_CORE_BRANCH_NAME, HEAD_CORE_BRANCH_NAME, BASE_RULE_BRANCH_NAME,
                                  HEAD_RULE_BRANCH_NAME, args.use_rule_compare)


def resolve_core_branch_file_name(core_base_branch_name, core_head_branch_name, rules_base_branch_name, rules_head_branch_name, rule_compare):
    global BASE_BRANCH_FILE_NAME, HEAD_BRANCH_FILE_NAME

    if rule_compare:
        BASE_BRANCH_FILE_NAME = rules_base_branch_name
        HEAD_BRANCH_FILE_NAME = rules_head_branch_name
    else:
        BASE_BRANCH_FILE_NAME = core_base_branch_name
        HEAD_BRANCH_FILE_NAME = core_head_branch_name


def get_core_branch(base_branch, head_branch, rules_branch_base, rules_branch_head):
    if base_branch is None and head_branch is None:
        if rules_branch_base == 'main' and rules_branch_head == 'dev':
            return ['main', 'main']
        else:
            return ['dev', 'dev']
    else:
        return [base_branch, head_branch]


def get_rules_branch(base_branch, head_branch, rules_branch_base, rules_branch_head):
    if rules_branch_base is None and rules_branch_head is None:
        if base_branch == 'main':
            return ['main', 'dev']
        elif head_branch == 'main':
            return ['dev', 'main']
        return ['dev', 'dev']
    else:
        return [rules_branch_base, rules_branch_head]