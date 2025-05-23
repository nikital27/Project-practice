import environs

env = environs.Env()
env.read_env()

with env.prefixed('TELEGRAM_BOT_'):
    TOKEN = env.str('TOKEN')
    DROP_PENDING_UPDATES = env.bool('DROP_PENDING_UPDATES')
    DEBUG = env.bool('DEBUG')

    if not DEBUG:
        DB_USER = env.str('DB_USER')
        DB_PASSWORD = env.str('DB_PASSWORD')
        DB_ADDRESS = env.str('DB_ADDRESS')
        DB_PORT = env.int('DB_PORT')
        DB_NAME = env.str('DB_NAME')

        REDIS_HOST = env.str('REDIS_HOST')
        REDIS_PORT = env.int('REDIS_PORT')

        REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

DB_URL = (
    'sqlite:///travel_agent.db'
    if DEBUG
    else f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@'
    f'{DB_ADDRESS}:{DB_PORT}/{DB_NAME}'
)
