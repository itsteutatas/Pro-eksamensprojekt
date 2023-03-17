from twitchio.ext import commands, routines
import asyncio
import dbconfig as dbcfg
import oauthconfig as oauth
import aiomysql

class giveaways():
    async def start(self):
        conn = await aiomysql.connect(dbcfg.localconfig["host"], dbcfg.localconfig["user"], dbcfg.localconfig["password"], dbcfg.localconfig["db"])

        print("connected")

        cur = await conn.cursor()
        await cur.execute("DROP Table participants")
        await cur.execute(f"CREATE table participants(participantID int NOT NULL AUTO_INCREMENT,participantNAME VARCHAR(60),PRIMARY KEY (participantID))")
        await conn.commit()
        conn.close()

    async def participate(self):

        conn = await aiomysql.connect(dbcfg.localconfig["host"], dbcfg.localconfig["user"], dbcfg.localconfig["password"], dbcfg.localconfig["db"])
        cur = await conn.cursor()

        await cur.execute(f"SELECT * from participants where participantNAME = {probot.name}")
        if cur.fetchall():
            pass
        else:
            await cur.execute(f"INSERT INTO participants(participantID, participantNAME) VALUES (0, {probot.name})")

        await conn.commit()

        conn.close()

    async def end(self):
        conn = await aiomysql.connect(dbcfg.localconfig["host"], dbcfg.localconfig["user"], dbcfg.localconfig["password"], dbcfg.localconfig["db"])
        cur = await conn.cursor()

        await cur.execute("SELECT participantNAME FROM participants ORDER BY RAND() LIMIT 1")
        winner = await cur.fetchone()
        await conn.commit()

        conn.close()
        return winner



class probot(commands.Bot):
    giveaway_bool = False

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=oauth.oauth, prefix='!', initial_channels=['teutatas'])

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def name(self):
        return str(self.name)


    # final state [shoutout command]
    @commands.command()
    async def so(self, ctx: commands.Context, name: str):
        print('test')

        await ctx.send(f"Check out {name} over at twitch.tv/{name}")

    # final state [discord command]
    @commands.command()
    async def discord(self, ctx: commands.Context):
        print('test')
        await ctx.send("https://discord.gg/FeajQPq4TZ")

    # teststate [giveaway]
    @commands.command()
    async def giveaway(self, ctx: commands.Context):
        if self.giveaway_bool:
            await ctx.send(f'Giveaway already running')
        else:
            if ctx.author.name == 'teutatas':
                await ctx.send(f'GivePLZ Giveaway TakeNRG')
                await giveaways.start(self)
                self.giveaway_bool = True
                return

    @commands.command()
    async def endgiveaway(self, ctx: commands.Context):
        if ctx.author.name == 'teutatas':
            if not self.giveaway_bool:
                ctx.send(f'No giveaway running')
            else:
                use = str(giveaways.end)
                use = use.replace('(', '')
                use = use.replace(',)', '')
                await ctx.send(f'TakeNRG Congratulations {use} you won the giveaway GivePLZ')
                self.giveaway_bool = False
                return

    @commands.command()
    async def join(self, ctx: commands.Context):
        if self.giveaway_bool == True:
            name = ctx.author
            print('test1')
            await giveaways.participate(giveaways())
            print('test2')
            self.name = name



bot = probot()
bot.run()