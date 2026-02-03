import discord
import asyncio
from config.Config import DISCORD_TOKEN
from command.Command import load_extension
from discord.ext import commands
from manager.GuildManager import GuildManager
from service.AudioService import stop, next, play

intents=discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents = intents)
guild_manager = GuildManager.get_instance()
        

async def main():
    async with bot:
        await load_extension(bot)
        await bot.start(DISCORD_TOKEN)

@bot.event
async def on_ready():
    print('Running...') 

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel:
        if len(before.channel.members) == 1:
            await member.guild.voice_client.disconnect()
            
# チャットを検出
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 現在クイズ中か確認
    try:
        qm = guild_manager.get_quiz_manager(message.guild.id)
    except Exception:
        return
    
    if qm.is_quiz_active == False or qm.is_question_playing == False:
        return
    
    target_channel = qm.target_channel
    if target_channel is not None and message.channel != target_channel:
        return

    content = message.content.strip()
    correct_answer = qm.youtube_urls[qm.current_question_index][1]
    if content.lower() == correct_answer.lower():
        qm.add_participant_point(message.author.id)
        await stop(message.guild)
        await message.channel.send(f"{message.author.mention} さん、正解です！")
        await next(message.guild, bot)
        


if __name__ == "__main__":
    asyncio.run(main())