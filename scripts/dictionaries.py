import string
import random
import datetime

GENERIC_KEYWORDS = [
    "tool", "app", "service", "bot", "script", "util", "helper", "system", "engine", "platform",
    "manager", "controller", "daemon", "monitor", "agent", "client", "server", "api", "wrapper",
    "interface", "module", "library", "framework", "toolkit", "package", "bundle", "plugin",
    "extension", "addon", "driver", "provider", "handler", "processor", "parser", "generator",
    "builder", "creator", "compiler", "interpreter", "runtime", "vm", "emulator", "simulator",
    "viewer", "editor", "ide", "gui", "ui", "cli", "shell", "console", "terminal", "prompt",
    "dashboard", "panel", "widget", "component", "element", "control", "form", "view", "page",
    "template", "theme", "layout", "style", "css", "html", "web", "site", "blog", "portfolio",
    "wiki", "docs", "guide", "tutorial", "example", "demo", "sample", "test", "spec", "benchmark",
    "sandbox", "playground", "experiment", "prototype", "draft", "concept", "idea", "proposal",
    "project", "repo", "source", "code", "base", "core", "main", "root", "hub", "node", "link",
    "bridge", "gateway", "proxy", "router", "switch", "hub", "network", "mesh", "grid", "cluster",
    "farm", "pool", "queue", "stack", "heap", "tree", "graph", "list", "array", "map", "set",
    "dict", "hash", "cache", "store", "db", "database", "sql", "nosql", "kv", "file", "disk",
    "storage", "volume", "drive", "fs", "system", "os", "kernel", "driver", "patch", "fix",
    "hack", "mod", "tweak", "script", "snippet", "gist", "paste", "bin", "archive", "backup",
    "log", "trace", "metric", "stat", "analytics", "report", "summary", "alert", "notification",
    "message", "mail", "email", "sms", "push", "hook", "webhook", "event", "trigger", "action",
    "task", "job", "worker", "thread", "process", "coroutine", "async", "sync", "lock", "mutex",
    "semaphore", "signal", "timer", "clock", "time", "date", "calendar", "schedule", "cron",
    "auth", "login", "signup", "register", "session", "token", "jwt", "oauth", "sso", "saml",
    "security", "crypto", "hash", "cipher", "encrypt", "decrypt", "sign", "verify", "key",
    "cert", "ssl", "tls", "https", "proxy", "vpn", "firewall", "router", "loadbalancer", "cdn",
    "dns", "ip", "tcp", "udp", "http", "ftp", "ssh", "telnet", "smtp", "pop3", "imap", "rest",
    "graphql", "soap", "rpc", "grpc", "websocket", "socket", "port", "host", "domain", "url",
    "uri", "path", "route", "endpoint", "resource", "entity", "model", "schema", "type", "class",
    "object", "instance", "struct", "record", "tuple", "enum", "union", "variant", "any", "unknown",
    "void", "null", "nil", "none", "true", "false", "bool", "int", "float", "double", "string",
    "char", "byte", "bit", "buffer", "stream", "reader", "writer", "parser", "serializer",
    "deserializer", "encoder", "decoder", "marshaller", "unmarshaller", "validator", "sanitizer",
    "formatter", "linter", "minifier", "bundler", "compiler", "transpiler", "interpreter"
]

TECH_STACK_TERMS = [
    "django", "react", "spring", "flask", "express", "nodejs", "vue", "angular", "svelte",
    "nextjs", "nuxtjs", "gatsby", "rails", "laravel", "symfony", "fastapi", "gin", "echo",
    "fiber", "actix", "rocket", "axum", "warp", "tokio", "asyncio", "celery", "sidekiq",
    "redis", "memcached", "rabbitmq", "kafka", "pulsar", "nats", "zeromq", "grpc", "graphql",
    "apollo", "relay", "prisma", "typeorm", "sequelize", "mongoose", "hibernate", "jpa",
    "entityframework", "dapper", "mybatis", "sqlalchemy", "peewee", "alembic", "flyway",
    "liquibase", "docker", "kubernetes", "helm", "terraform", "ansible", "chef", "puppet",
    "vagrant", "packer", "jenkins", "gitlab", "github", "bitbucket", "travis", "circleci",
    "aws", "azure", "gcp", "heroku", "netlify", "vercel", "cloudflare", "digitalocean",
    "linode", "vultr", "firebase", "supabase", "appwrite", "auth0", "okta", "cognito",
    "stripe", "paypal", "braintree", "twilio", "sendgrid", "mailgun", "mailchimp", "slack",
    "discord", "telegram", "whatsapp", "wechat", "line", "messenger", "twitter", "facebook",
    "instagram", "linkedin", "tiktok", "youtube", "twitch", "spotify", "apple", "google",
    "microsoft", "amazon", "meta", "netflix", "openai", "anthropic", "cohere", "huggingface",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "scipy", "matplotlib",
    "seaborn", "plotly", "dash", "streamlit", "gradio", "jupyter", "colab", "kaggle",
    "spark", "hadoop", "flink", "storm", "hive", "presto", "trino", "snowflake", "bigquery",
    "redshift", "athena", "elasticsearch", "solr", "lucene", "algolia", "meilisearch",
    "typesense", "qdrant", "milvus", "pinecone", "weaviate", "neo4j", "arangodb", "couchbase",
    "couchdb", "mongodb", "cassandra", "scylladb", "dynamodb", "cosmosdb", "firestore",
    "mysql", "postgresql", "sqlite", "mariadb", "oracle", "sqlserver", "db2", "sybase",
    "informix", "teradata", "netezza", "vertica", "greenplum", "clickhouse", "druid",
    "pinot", "influxdb", "timescaledb", "prometheus", "grafana", "kibana", "logstash",
    "fluentd", "filebeat", "telegraf", "datadog", "newrelic", "dynatrace", "appdynamics",
    "sentry", "rollbar", "bugsnag", "raygun", "honeybadger", "pagerduty", "opsgenie",
    "victorops", "splunk", "sumologic", "loggly", "papertrail", "graylog", "elk", "efk",
    "jamstack", "mean", "mern", "mevn", "lamp", "lemp", "wamp", "mamp", "xampp", "serverless",
    "microservices", "monolith", "pwa", "spa", "ssr", "ssg", "isr", "api", "rest", "soap",
    "rpc", "xml", "json", "yaml", "toml", "ini", "csv", "tsv", "parquet", "orc", "avro",
    "protobuf", "thrift", "flatbuffers", "capnproto", "msgpack", "bson", "cbor", "smile"
]

ADJECTIVES_NOUNS = [
    "smart", "fast", "awesome", "data", "cloud", "magic", "super", "hyper", "ultra", "mega",
    "giga", "tera", "peta", "exa", "zeta", "yotta", "micro", "nano", "pico", "femto", "atto",
    "zepto", "yocto", "quantum", "cyber", "techno", "electro", "mechano", "bio", "neuro",
    "astro", "cosmo", "geo", "hydro", "aero", "pyro", "cryo", "photo", "chrono", "spatio",
    "sonic", "optic", "haptic", "kinetic", "static", "dynamic", "fluid", "solid", "gas",
    "plasma", "crystal", "metal", "wood", "stone", "earth", "water", "fire", "air", "wind",
    "storm", "thunder", "lightning", "rain", "snow", "ice", "frost", "sun", "moon", "star",
    "planet", "galaxy", "universe", "space", "time", "dimension", "portal", "gateway",
    "bridge", "wall", "door", "window", "roof", "floor", "room", "house", "city", "world",
    "life", "death", "mind", "soul", "spirit", "ghost", "phantom", "shadow", "light", "dark",
    "black", "white", "red", "green", "blue", "yellow", "cyan", "magenta", "orange", "purple",
    "pink", "brown", "gray", "silver", "gold", "copper", "iron", "steel", "bronze", "brass",
    "ruby", "sapphire", "emerald", "diamond", "pearl", "opal", "jade", "onyx", "quartz",
    "topaz", "amethyst", "garnet", "beryl", "zircon", "spinel", "tourmaline", "peridot",
    "agatel", "jasper", "turquoise", "lapis", "malachite", "azurite", "fluorite", "calcite",
    "lion", "tiger", "bear", "wolf", "fox", "eagle", "hawk", "falcon", "owl", "raven",
    "crow", "swan", "duck", "goose", "shark", "whale", "dolphin", "seal", "penguin", "turtle",
    "snake", "lizard", "frog", "toad", "spider", "scorpion", "crab", "lobster", "octopus",
    "squid", "snail", "slug", "worm", "ant", "bee", "wasp", "fly", "mosquito", "butterfly",
    "moth", "beetle", "bug", "dragon", "unicorn", "griffin", "phoenix", "chimera", "hydra",
    "kraken", "leviathan", "behemoth", "golem", "troll", "goblin", "orc", "elf", "dwarf",
    "giant", "titan", "god", "demon", "angel", "devil", "monster", "beast", "creature",
    "mutant", "alien", "cyborg", "robot", "android", "machine", "engine", "motor", "pump",
    "valve", "pipe", "tube", "wire", "cable", "chain", "rope", "string", "thread", "yarn"
]

PROGRAMMING_LANGUAGES = [
    "python", "javascript", "go", "rust", "cpp", "java", "ruby", "php", "csharp", "swift",
    "kotlin", "typescript", "scala", "dart", "elixir", "clojure", "haskell", "lua", "perl",
    "r", "matlab", "shell", "powershell", "objective-c", "groovy", "julia", "fsharp", "vb",
    "assembly", "cobol", "fortran", "ada", "lisp", "prolog", "scheme", "erlang", "ocaml",
    "crystal", "nim", "zig", "v", "solidity", "vyper", "haxe", "reason", "purescript",
    "elm", "coffeescript", "actionscript", "coldfusion", "delphi", "pascal", "awk", "sed"
]

def generate_random_query():
    strategies = [
        "generic_keyword",
        "tech_stack",
        "adjective_noun",
        "two_letter",
        "three_letter",
        "language_only"
    ]
    strategy = random.choice(strategies)

    query_parts = []

    if strategy == "generic_keyword":
        query_parts.append(random.choice(GENERIC_KEYWORDS))
    elif strategy == "tech_stack":
        query_parts.append(random.choice(TECH_STACK_TERMS))
    elif strategy == "adjective_noun":
        query_parts.append(random.choice(ADJECTIVES_NOUNS))
    elif strategy == "two_letter":
        query_parts.append(''.join(random.choices(string.ascii_lowercase, k=2)))
    elif strategy == "three_letter":
        query_parts.append(''.join(random.choices(string.ascii_lowercase, k=3)))
    elif strategy == "language_only":
        pass # Language will be added below

    if random.random() < 0.7:
        lang = random.choice(PROGRAMMING_LANGUAGES)
        query_parts.append(f"language:{lang}")

    if random.random() < 0.5:
        # random date between 2015 and today
        start_date = datetime.date(2015, 1, 1)
        end_date = datetime.date.today()
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days

        # created vs pushed
        date_type = random.choice(["created", "pushed"])

        # generate a random range
        random_number_of_days = random.randrange(days_between_dates)
        random_start = start_date + datetime.timedelta(days=random_number_of_days)

        # span between 1 month and 1 year
        span_days = random.randint(30, 365)
        random_end = random_start + datetime.timedelta(days=span_days)
        if random_end > end_date:
            random_end = end_date

        query_parts.append(f"{date_type}:{random_start.strftime('%Y-%m-%d')}..{random_end.strftime('%Y-%m-%d')}")

    if not query_parts:
        query_parts.append(random.choice(GENERIC_KEYWORDS))

    return "+".join(query_parts)
