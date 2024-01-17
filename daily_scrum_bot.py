import os

import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from datetime import datetime, time, timedelta

server_id = 1195645316628742234
daily_scrum_channel_id = 1195957938305642567

daily_scrum_notice = "오전 11:00까지 업로드 해주세요 :grinning:"
daily_scrum_template = """* 데일리 스크럼 양식
```
1. 어제 한 일 :crescent_moon:
-
2. 오늘 할 일 :fire:
-
3. 공유할 이슈 :raised_hands:
-
```
"""


class DailyScrumBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync(guild=discord.Object(id=server_id))
        print(f"Synced slah commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        if 'already launched' in error.args[0]:
            await ctx.send("이미 실행 중입니다", ephemeral=True)
        else:
            await ctx.send(error, ephemeral=True)


bot = DailyScrumBot()


@bot.hybrid_command(name="hi", with_app_command=True, description="반가워요")
@app_commands.guilds(discord.Object(id=server_id))
async def hi(ctx: commands.Context):
    await ctx.reply("안녕하세요. Swifty팀의 데일리 스크럼 봇이에요 :robot:", ephemeral=True)


@bot.hybrid_command(name="알림시작", with_app_command=True, description="데일리 스크럼 알림 시작")
@app_commands.guilds(discord.Object(id=server_id))
async def start_daily_scrum(ctx: commands.Context):
    await ctx.reply("데일리 스크럼 알림을 시작합니다", ephemeral=True)
    write_daily_scrum_template.start()


@bot.hybrid_command(name="알림종료", with_app_command=True, description="데일리 스크럼 알림 종료")
@app_commands.guilds(discord.Object(id=server_id))
async def stop_daily_scrum(ctx: commands.Context):
    await ctx.reply("데일리 스크럼 알림을 종료합니다", ephemeral=True)
    write_daily_scrum_template.cancel()


@tasks.loop(hours=23, minutes=59, seconds=55)
async def write_daily_scrum_template():
    current_datetime = datetime.now()
    target_time = time(23, 0, 0)  # UTC 기준 23:00 / 한국시간으로 오전 08:00

    if target_time < current_datetime.time() <= time(23, 59, 59):
        target_datetime = datetime.combine(current_datetime.date() + timedelta(days=1), target_time)
    else:
        target_datetime = datetime.combine(current_datetime.date(), target_time)

    print(f"다음 알림 시각: (UTC) {target_datetime}")
    time_interval = (target_datetime - current_datetime).total_seconds()
    print(f"{time_interval}초 뒤 알림 예정입니다")
    await asyncio.sleep(time_interval)

    daily_scrum_channel = bot.get_channel(daily_scrum_channel_id)
    if (daily_scrum_channel):
        thread_name = (target_datetime + timedelta(days=1)).strftime("%Y-%m-%d 데일리 스크럼")  # UTC 보정 +1일
        thread = await daily_scrum_channel.create_thread(name=thread_name)
        thread_link = thread.jump_url
        
        await daily_scrum_channel.send(
            content=f"오늘 하루도 화이팅입니다! {thread_link}"
        )
        await thread.send(daily_scrum_template)


bot.run(os.getenv('DISCORD_TOKEN'))
