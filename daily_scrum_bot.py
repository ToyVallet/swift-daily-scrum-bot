import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio, os
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

server_id = 1195645316628742234
daily_scrum_channel_id = 1195957938305642567
daily_scrum_template = """해가 밝았어요 :grinning:

* 데일리 스크럼 양식
```
### 어제 한 일 :crescent_moon:
-
### 오늘 할 일 :fire:
-
### 공유할 이슈 :raised_hands:
-
```
"""
KST = ZoneInfo("Asia/Seoul")

notification_schedule = {}


class DailyScrumBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync(guild=discord.Object(id=server_id))

    async def on_command_error(self, ctx, error):
        await ctx.send(error, ephemeral=True)


bot = DailyScrumBot()


@bot.event
async def on_ready():
    # 무료 호스팅 서버가 몇분동안 idle 상태면 맘대로 재부팅해버려서 프로그램 시작과 동시에 알람 시작해야함
    # print("알람을 자동으로 시작합니다")
    write_daily_scrum_template.start()


@bot.hybrid_command(name="hi", with_app_command=True, description="반가워요")
@app_commands.guilds(discord.Object(id=server_id))
async def hi(ctx: commands.Context):
    await ctx.reply("안녕하세요. Swifty팀의 데일리 스크럼 봇이에요 :robot:", ephemeral=True)


@bot.hybrid_command(name="알림시작",
                    with_app_command=True,
                    description="데일리 스크럼 알림 시작")
@app_commands.guilds(discord.Object(id=server_id))
async def start_daily_scrum(ctx: commands.Context):
    if write_daily_scrum_template.is_running() == True:
        await ctx.reply("이미 실행 중입니다", ephemeral=True)
        return

    await ctx.reply("데일리 스크럼 알림을 시작합니다", ephemeral=True)
    write_daily_scrum_template.start()


@bot.hybrid_command(name="알림종료",
                    with_app_command=True,
                    description="데일리 스크럼 알림 종료")
@app_commands.guilds(discord.Object(id=server_id))
async def stop_daily_scrum(ctx: commands.Context):
    await ctx.reply("데일리 스크럼 알림을 종료합니다", ephemeral=True)
    write_daily_scrum_template.cancel()
    notification_schedule.clear()


@tasks.loop(hours=12)
async def write_daily_scrum_template():
    current_datetime = datetime.now(tz=KST)

    target_time = time(8, 0, 0, tzinfo=KST)

    if target_time < current_datetime.time() <= time(23, 59, 59):
        target_datetime = datetime.combine(current_datetime.date() +
                                           timedelta(days=1),
                                           target_time,
                                           tzinfo=KST)
    else:
        target_datetime = datetime.combine(current_datetime.date(),
                                           target_time,
                                           tzinfo=KST)
    # print(f"current: {current_datetime}, target: {target_datetime}")

    if notification_schedule.get(target_datetime) is not None:
        # print(f"{target_datetime}에 이미 알림이 예약 되어 있습니다")
        await asyncio.sleep(30)
        write_daily_scrum_template.restart()
        return

    notification_schedule[target_datetime] = True
    time_interval = (target_datetime - current_datetime).total_seconds()
    if time_interval < 0:
        # print("알림 날짜가 과거입니다")
        write_daily_scrum_template.restart()
        return

    # print(f"다음 알림 시각: {target_datetime}")
    # print(f"{time_interval}초 뒤 알림 예정입니다")
    await asyncio.sleep(time_interval)

    daily_scrum_channel = bot.get_channel(daily_scrum_channel_id)
    if daily_scrum_channel:
        thread_name = target_datetime.strftime("%Y-%m-%d 데일리 스크럼")
        thread = await daily_scrum_channel.create_thread(
            name=thread_name, type=discord.ChannelType.public_thread)
        thread_link = thread.jump_url

        await daily_scrum_channel.send(content=f"오늘 하루도 화이팅입니다! {thread_link}")
        await thread.send(daily_scrum_template)


def main():
    bot.run(os.environ['DISCORD_TOKEN'])


if __name__ == '__main__':
    main()
