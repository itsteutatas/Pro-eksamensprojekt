from typing import Any

from twitchio.ext import commands, routines
import asyncio
import aiomysql

import dbconfig as dbcfg
import oauthconfig as oauth
import config as cfg




class probot(commands.Bot):


    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=oauth.oauth, prefix='!', initial_channels=cfg.i_channel_list)
        self.giveaway_bool = False


        # Set up the database connection and create the participants table if it doesn't exist
        self.loop.create_task(self.setup_database())

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def setup_database(self):
        conn = await aiomysql.connect(dbcfg.localconfig["host"], dbcfg.localconfig["user"], dbcfg.localconfig["password"], dbcfg.localconfig["db"])
        curr = await conn.cursor()

        print("connected")

        await curr.execute("SELECT * FROM participants")
        result = await curr.fetchall()
        print(result)

        await curr.execute("DROP TABLE IF EXISTS participants")
        await curr.execute(f"CREATE TABLE participants(participantID int NOT NULL AUTO_INCREMENT,participantNAME VARCHAR(60),PRIMARY KEY (participantID))")
        await conn.commit()
        conn.close()

    async def add_participant(self, participant_name):
        conn = await aiomysql.connect(dbcfg.localconfig["host"], dbcfg.localconfig["user"], dbcfg.localconfig["password"], dbcfg.localconfig["db"])
        curr = await conn.cursor()

        # Check if the participant already exists in the table
        await curr.execute("SELECT * FROM participants WHERE participantNAME = %s", (participant_name,))
        result = await curr.fetchall()
        if len(result) > 0:
            # Participant already exists, do nothing
            pass
        else:
            # Participant does not exist, add them to the table
            await curr.execute(f"INSERT INTO participants(participantID, participantNAME) VALUES (0, %s)", (participant_name,))

        await conn.commit()
        conn.close()

    async def get_winner(self):
        conn = await aiomysql.connect(dbcfg.localconfig["host"], dbcfg.localconfig["user"], dbcfg.localconfig["password"], dbcfg.localconfig["db"])
        curr = await conn.cursor()

        await curr.execute("SELECT participantNAME FROM participants ORDER BY RAND() LIMIT 1")
        winner = await curr.fetchone()

        await conn.commit()
        conn.close()

        return winner

    # final state [shoutout command]
    @commands.command(name='so')
    async def shoutout(self, ctx: commands.Context, name: str):
        await ctx.send(f'Check out {name} over at twitch.tv/{name}')

    @commands.command()
    async def test(self, ctx: commands.Context):
        await ctx.send(f'test')

    # final state [discord command]
    @commands.command()
    async def discord(self, ctx: commands.Context):
        print('test')
        await ctx.send("https://discord.gg/a3jHXau")

    # teststate [giveaway]
    @commands.command()
    async def giveaway(self, ctx: commands.Context):
        await self.setup_database()
        if self.giveaway_bool:
            await ctx.send(f'Giveaway already running')
        else:
            if ctx.author.name in cfg.admin_n_list:
                await ctx.send(f'GivePLZ Giveaway TakeNRG')
                self.giveaway_bool = True
                return

    @commands.command()
    async def endgiveaway(self, ctx: commands.Context):
        if ctx.author.name in cfg.admin_n_list:
            # Check if a giveaway is currently active
            if not self.giveaway_bool:
                await ctx.send('There is currently no active giveaway.')
                return

            # Pick a winner from the list of participants
            winner = await self.get_winner()
            winner = str(winner).translate( { ord(i): None for i in "'(),"} )
            # Announce the winner in chat
            await ctx.send(f'Congratulations {winner}! You have won the test!')

            # Reset the giveaway state
            self.giveaway_bool = False
            self.get_winner = []

    @commands.command(name='join')
    async def join_giveaway(self, ctx: commands.Context):
        participant_name = ctx.author.name
        await self.add_participant(participant_name)




bot = probot()
bot.run()