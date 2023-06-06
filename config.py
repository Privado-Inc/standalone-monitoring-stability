BASE_CORE_BRANCH_NAME = None
HEAD_CORE_BRANCH_NAME = None

BASE_RULE_BRANCH_NAME = None
HEAD_RULE_BRANCH_NAME = None

BASE_CORE_BRANCH_KEY = None
HEAD_CORE_BRANCH_KEY = None

BASE_SHEET_BRANCH_NAME = None
HEAD_SHEET_BRANCH_NAME = None

BASE_PRIVADO_CORE_URL = None
HEAD_PRIVADO_CORE_URL = None

BASE_PRIVADO_CORE_OWNER = None
HEAD_PRIVADO_CORE_OWNER = None

BASE_PRIVADO_RULE_URL = None
HEAD_PRIVADO_RULE_URL = None

BASE_PRIVADO_RULE_OWNER = None
HEAD_PRIVADO_RULE_OWNER = None

SLACK_SUMMARY_FILE_NAME = "slack_summary.txt"
OUTPUT_FILE_NAME = "output.xlsx"
PRIVADO_CORE_URL = "https://github.com/Privado-Inc/privado-core"
PRIVADO_RULE_URL = "https://github.com/Privado-Inc/privado"


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

    resolve_privado_core_repo(args.base_core_repo, args.head_core_repo)
    resolve_privado_rule_repo(args.base_rule_repo, args.head_rule_repo)

    resolve_core_branch_key_name(BASE_CORE_BRANCH_NAME, HEAD_CORE_BRANCH_NAME, BASE_RULE_BRANCH_NAME,
                                 HEAD_RULE_BRANCH_NAME, args.use_rule_compare, BASE_PRIVADO_CORE_OWNER,
                                 HEAD_PRIVADO_CORE_OWNER, BASE_PRIVADO_RULE_OWNER, HEAD_PRIVADO_RULE_OWNER)


def resolve_core_branch_key_name(core_base_branch_name, core_head_branch_name, rules_base_branch_name, rules_head_branch_name, rule_compare, base_core_owner, head_core_owner, base_rule_owner, head_rule_owner):
    global BASE_CORE_BRANCH_KEY, HEAD_CORE_BRANCH_KEY, BASE_SHEET_BRANCH_NAME, HEAD_SHEET_BRANCH_NAME

    BASE_CORE_BRANCH_KEY = f'{base_core_owner}-{core_base_branch_name}#{base_rule_owner}-{rules_base_branch_name}'
    HEAD_CORE_BRANCH_KEY = f'{head_core_owner}-{core_head_branch_name}#{head_rule_owner}-{rules_head_branch_name}'

    if rule_compare:
        BASE_SHEET_BRANCH_NAME = rules_base_branch_name
        HEAD_SHEET_BRANCH_NAME = rules_head_branch_name
    else:
        BASE_SHEET_BRANCH_NAME = core_base_branch_name
        HEAD_SHEET_BRANCH_NAME = core_head_branch_name


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


def init_file():
    global BASE_CORE_BRANCH_NAME, HEAD_CORE_BRANCH_NAME, BASE_CORE_BRANCH_KEY, HEAD_CORE_BRANCH_KEY, \
        BASE_SHEET_BRANCH_NAME, HEAD_SHEET_BRANCH_NAME

    BASE_CORE_BRANCH_NAME = BASE_CORE_BRANCH_KEY = BASE_SHEET_BRANCH_NAME = 'first'
    HEAD_CORE_BRANCH_NAME = HEAD_CORE_BRANCH_KEY = HEAD_SHEET_BRANCH_NAME = 'second'

def resolve_privado_core_repo(base_repo, head_repo):
    global BASE_PRIVADO_CORE_OWNER, HEAD_PRIVADO_CORE_OWNER, BASE_PRIVADO_CORE_URL, HEAD_PRIVADO_CORE_URL
    if base_repo == 'NA' or head_repo == 'NA':
        BASE_PRIVADO_CORE_URL = PRIVADO_CORE_URL
        HEAD_PRIVADO_CORE_URL = PRIVADO_CORE_URL
        BASE_PRIVADO_CORE_OWNER = 'privado-core'
        HEAD_PRIVADO_CORE_OWNER = 'privado-core'
    else:
        BASE_PRIVADO_CORE_URL = base_repo
        HEAD_PRIVADO_CORE_URL = head_repo
        BASE_PRIVADO_CORE_OWNER = get_repo_owner(base_repo)
        HEAD_PRIVADO_CORE_OWNER = get_repo_owner(head_repo)


def resolve_privado_rule_repo(base_repo, head_repo):
    global BASE_PRIVADO_RULE_OWNER, HEAD_PRIVADO_RULE_OWNER, BASE_PRIVADO_RULE_URL, HEAD_PRIVADO_RULE_URL

    if base_repo == 'NA' or head_repo == 'NA':
        BASE_PRIVADO_RULE_URL = PRIVADO_RULE_URL
        HEAD_PRIVADO_RULE_URL = PRIVADO_RULE_URL
        BASE_PRIVADO_RULE_OWNER = 'privado'
        HEAD_PRIVADO_RULE_OWNER = 'privado'
    else:
        BASE_PRIVADO_RULE_URL = base_repo
        HEAD_PRIVADO_RULE_URL = head_repo
        BASE_PRIVADO_RULE_OWNER = get_repo_owner(base_repo)
        HEAD_PRIVADO_RULE_OWNER = get_repo_owner(head_repo)

def get_repo_owner(url):
    parts = url.split('/')
    return parts[-2]
