INITIAL_EXTENSIONS = [
    'command.startCommand',
    'command.leaveCommand',
]

async def load_extension(bot):
    for cog in INITIAL_EXTENSIONS:
        await bot.load_extension(cog)