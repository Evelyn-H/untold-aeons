import asyncio
import functools
import discord

from . import colors
from . import coc
from . import ua
from . import dark
from . import npc
from . import roll

class Command:
    def __init__(self, function, prefix, add_footer, require_space):
        self.function = function
        self.prefix = prefix
        self.add_footer = add_footer
        self.require_space = require_space

    def __call__(self, message):
        return self.function(message)

# the difference here is that it also takes all the discord metadata about the message
# *and* that it's async so it can do fancy discord shenanigans
class FancyCommand(Command):
    async def __call__(self, message, meta_message):
        return await self.function(message, meta_message)

class Bot:
    def __init__(self):
        self.commands = []

    def register_command(self, func, prefix, add_footer=True, fancy=False, require_space=True):
        if fancy:
            self.commands.append(FancyCommand(func, prefix, add_footer, require_space))
        else:
            self.commands.append(Command(func, prefix, add_footer, require_space))

    # command decorator
    def command(self, prefix, add_footer=True):
        """
        The decorated function can return either a string or a dict with the optional fields of `title`, `description`, and `color`.
        """
        def actual_decorator(func):
            self.register_command(func, prefix, add_footer)
            @functools.wraps(func)
            def wrapper(message):
                return func(message)
            return wrapper
        return actual_decorator

    async def on_message(self, message):
        search_list = []
        for command in self.commands:
            if isinstance(command.prefix, list):
                search_list.extend([(prefix, command) for prefix in command.prefix])
            else:
                search_list.append((command.prefix, command))
        search_list.sort(key=lambda x: len(x[0]), reverse=True)

        error = None
        for prefix, command in search_list:
            if (arguments := self._parse_command(message, prefix, command.require_space)) is not None:
                # debug log
                print(f"Message received: {message.content}")
                print(f"Running command <{prefix}>")

                # log channel stuff
                log_channel = discord.utils.get(message.guild.channels, name='ua-log')
                if log_channel:
                    await log_channel.send(
                        f"`{message.content}` by {message.author.mention} in {message.channel.mention}",
                        allowed_mentions=discord.AllowedMentions.none(),
                        # reference=message   # discord.py >=1.6 only
                    )

                # run the command processor
                try:
                    if isinstance(command, FancyCommand):
                        return_message = await command(arguments, meta_message=message)
                    else:
                        return_message = command(arguments)
                except Exception as e:
                    return_message = "Something went wrong, go yell at <@!139111840364888064>"
                    error = e

                # only do something if we have a return value
                if not return_message is None:
                    # embed
                    if isinstance(return_message, dict):
                        embed = discord.Embed.from_dict(return_message)
                        if command.add_footer:
                            embed.set_footer(text=f"@{message.author.display_name}")
                        await message.channel.send(embed=embed)

                    # just a regular string message
                    else:
                        await message.channel.send(str(return_message))
                    # don't have to search any further

                if error:
                    raise error
                
                return


    @staticmethod
    def _parse_command(message, prefix, require_space=True):
        # allow for "synonymous" commands
        # print(message.content, prefix)
        if isinstance(prefix, list):
            for p in prefix:
                if (value := Bot._parse_command(message, p)) is not None: # yay recursion!
                    return value
        else:
            if message.content.startswith(prefix + ' ') or message.content.rstrip() == prefix:
                return message.content[len(prefix)+1:].lstrip()
            if not require_space and message.content.startswith(prefix):
                return message.content[len(prefix):].lstrip()
