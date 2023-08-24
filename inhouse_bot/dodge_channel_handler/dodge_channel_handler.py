from typing import Optional, List
import discord
import sqlalchemy
from discord import TextChannel
from discord.ext.commands import Bot
from sqlalchemy import func

from inhouse_bot.database_orm import (
    ChannelInformation,
    session_scope,
    Player,
    PlayerRating,
    Game,
    GameParticipant,
)


class DodgeChannelHandler:
    def __init__(self):
        with session_scope() as session:
            session.expire_on_commit = False

            self._dodge_channels = (
                session.query(ChannelInformation.id, ChannelInformation.server_id)
                .filter(ChannelInformation.channel_type == "DODGE")
                .all()
            )

    @property
    def dodge_channels_ids(self) -> List[int]:
        return [c.id for c in self._dodge_channels]

    def get_server_dodge_channels(self, server_id: int) -> List[int]:
        return [c.id for c in self._dodge_channels if c.server_id == server_id]

    def mark_dodge_channel(self, channel_id, server_id):
        """
        Marks the given channel + server combo as a queue
        """
        channel = ChannelInformation(id=channel_id, server_id=server_id, channel_type="DODGE")
        with session_scope() as session:
            session.merge(channel)

        self._dodge_channels.append(channel)

    def unmark_dodge_channel(self, channel_id):

        with session_scope() as session:
            channel_query = session.query(ChannelInformation).filter(ChannelInformation.id == channel_id)
            channel_query.delete(synchronize_session=False)

        self._dodge_channels = [c for c in self._dodge_channels if c.id != channel_id]

    async def update_dodge_channels(self, bot: Bot, server_id: Optional[int]):
        if not server_id:
            channels_to_update = self.dodge_channels_ids
        else:
            channels_to_update = self.get_server_dodge_channels(server_id)

        for channel_id in channels_to_update:
            channel = bot.get_channel(channel_id)

            if not channel:  # Happens when the channel does not exist anymore
                self.unmark_dodge_channel(channel_id)  # We remove it for the future


    async def sendDodgeMessage(self,playerName,playerId,bot):
        print("dodge channels")

        findServerId = str(self._dodge_channels[-1]).find('self.server_id=')
        findFinishServerId = str(self._dodge_channels[-1]).find('>')
        serverId = str(self._dodge_channels[-1])[findServerId+15:findFinishServerId]

        guild = bot.get_guild(int(serverId))
        dodgeChannelList = self.get_server_dodge_channels(int(serverId))
        print(self._dodge_channels)

        print(dodgeChannelList)
        message_text = "Match Queue Cancelled by Player: " + str(playerName) + " / ID: " + str(playerId)
        for channelId in dodgeChannelList:
            channel = guild.get_channel(channelId)

            # We save the message object in our local cache
            await channel.send(message_text)


dodge_channel_handler = DodgeChannelHandler()
