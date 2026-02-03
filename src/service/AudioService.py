import yt_dlp
import discord
import asyncio
from manager.GuildManager import GuildManager
from utils.QuizRandomizer import get_random_songs

from exception.Exception import *

guild_manager = GuildManager.get_instance()

async def join(interaction, num):
    if interaction.user.voice is None:
        raise UserNotJoinedException()
    
    if interaction.guild.voice_client and interaction.guild.voice_client.is_connected():
        raise AlreadyJoinedException()
    
    youtube_urls = get_random_songs(num)
    guild_manager.create_quiz_manager(interaction.guild.id, youtube_urls)
    await interaction.user.voice.channel.connect()

async def leave(interaction):
    if not(interaction.guild.voice_client and interaction.guild.voice_client.is_connected()):
        raise NotJoinedException()
    
    guild_manager.delete_quiz_manager(interaction.guild.id)
    await interaction.guild.voice_client.disconnect()

async def play(guild, url, bot):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            url = info_dict['url'] if 'url' in info_dict else info_dict['formats'][0]['url']

            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
            }

            source = discord.FFmpegPCMAudio(url, **ffmpeg_options)
            source = discord.PCMVolumeTransformer(source, volume=1.0)
            # 再生終了時は次の問題へ移行
            guild.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(next(guild, bot), bot.loop))

            # 30秒タイムアウト監視タスクを開始
            asyncio.create_task(_quiz_timeout_watchdog(guild, bot, 30))

    except Exception as e:
        print(f"Error: {e}")
        message = f"再生中にエラーが発生したため、次の問題に移行します。"
        qm = guild_manager.get_quiz_manager(guild.id)
        if qm.target_channel is not None:
            await qm.target_channel.send(message)
        await next(guild, bot)


async def _quiz_timeout_watchdog(guild, bot, timeout_seconds: int):
    await asyncio.sleep(timeout_seconds)
    try:
        qm = guild_manager.get_quiz_manager(guild.id)
    except Exception:
        return

    # 問題がまだ再生中であればタイムアップ処理
    if qm.is_question_playing:
        await stop(guild)

        # 次の問題へ（存在すれば再生を開始）
        try:
            await next(guild, bot)
        except Exception:
            pass

async def stop(guild):
    try:
        qm = guild_manager.get_quiz_manager(guild.id)
    except Exception:
        return
    """クイズの問題再生を停止する。"""
    try:
        if guild.voice_client and guild.voice_client.is_playing():
            guild.voice_client.stop()
    except Exception:
        pass

    try:
        await qm.end_quiz_song()
    except Exception:
        pass


async def next(guild, bot):
    """クイズで次の問題を開始する。"""
    try:
        qm = guild_manager.get_quiz_manager(guild.id)
    except Exception:
        return
    
    embed = discord.Embed(title=f"第{qm.current_question_index}問", description=f"正解は: {qm.youtube_urls[qm.current_question_index - 1][1]}, {qm.youtube_urls[qm.current_question_index - 1][0]} でした！", color=0x00ff00)
    await qm.target_channel.send(embed=embed)

    embed = discord.Embed(title=f"第{qm.current_question_index + 1}問", description="答えを"+ qm.target_channel.mention +"に入力してください！", color=0x00ff00)
    await qm.target_channel.send(embed=embed)

    # 次の問題のURLを取得して再生
    url = qm.start_quiz_song()
    if url is None:
        return

    await play(guild, url, bot)
