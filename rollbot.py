"""Simple PARANOIA Rollbot."""

import os
import re
import discord
from discord.ext import commands
import numpy as np

# Fetch the bot token from environment variables and ensure it's set
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
assert DISCORD_BOT_TOKEN is not None, 'DISCORD_BOT_TOKEN unset.'

# Initialize bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix='/', intents=intents)


def DiceRoll(sides: int, rolls: int) -> list:
  """Rolls a dice with the given number of sides for the specified number of times.

  Args:
      sides (int): Number of sides on the dice.
      rolls (int): Number of rolls to perform.

  Returns:
      list: List of roll results.
  """
  full_rolls = int(rolls)
  fractional_roll = rolls - full_rolls
  roll_results = []

  if full_rolls > 0:
    roll_results.extend(np.random.randint(1, sides + 1, full_rolls))

  if fractional_roll > 0:
    fractional_result = np.random.uniform(1, sides + 1) * fractional_roll
    roll_results.append(fractional_result)

  return roll_results


def DiceRollFromString(roll_string: str) -> str:
  """Parses a roll string and computes the roll results.

  Args:
      roll_string (str): String describing the rolls to perform.

  Returns:
      str: String describing the roll results.
  """
  roll_string = roll_string.strip().replace(' ', '')

  roll_expression, variables_expression = (
      roll_string.split(';') if ';' in roll_string else (roll_string, '')
  )

  dice_roll_expressions = re.findall(r'([\d\.]+)d([\d\.]+)', roll_expression)
  result_expression = roll_expression
  for expr in dice_roll_expressions:
    dice_count, dice_sides = map(float, expr)
    dice_results = DiceRoll(int(dice_sides), dice_count)
    result_expression = result_expression.replace(
        f'{expr[0]}d{expr[1]}', ' + '.join(map(str, dice_results)), 1
    )

  if variables_expression:
    variables = {
        var.split('=')[0].strip(): float(var.split('=')[1].strip())
        for var in variables_expression.split(',')
    }
    for var, value in variables.items():
      result_expression = result_expression.replace(var, str(value))

  result = np.sum([float(val) for val in result_expression.split(' + ')])
  if result == int(result):
    result = int(result)

  result_string = result_expression + f' = {result}'
  return f'{roll_string}: {result_string}'


@bot.event
async def on_ready():
  """Handles the event when the bot is ready.

  This function is called when the bot has successfully connected to the Discord
  server.
  """
  print(f'Logged in as {bot.user} (ID: {bot.user.id})')


@bot.group(name='roll')
async def roll_group(ctx):
  """Handles the /roll command group. Calls roll_single by default."""
  if ctx.message.author == bot.user:
    return

  if ctx.invoked_subcommand is None and not ctx.message.content.endswith('all'):
    await roll_single(ctx)


@roll_group.command(name='all')
async def roll_all(ctx, arg='1d20'):
  """Handles the /roll all command. Rolls dice for all present members."""
  print('roll_all')
  if ctx.message.author == bot.user:
    return
  await ctx.message.delete()

  present_members = []
  for member in ctx.guild.members:
    if (
        (
            member.status == discord.Status.online
            or member.status == discord.Status.idle
            or member.status == discord.Status.dnd
        )
        and not member.bot
        and member not in present_members
    ):
      present_members.append(member)

  roll_results = [
      '{} -> {}'.format(member.display_name, DiceRollFromString(arg))
      for member in present_members
  ]
  roll_result = '\n'.join(roll_results)
  await ctx.send(roll_result)


@roll_group.command(name='single')
async def roll_single(ctx, arg='1d20'):
  """Handles the /roll single command. Rolls dice for the command author."""
  print('roll_single')
  if ctx.message.author == bot.user:
    return

  await ctx.message.delete()
  await ctx.send(
      '{}: {}'.format(ctx.message.author.display_name, DiceRollFromString(arg))
  )


# Run the bot
bot.run(DISCORD_BOT_TOKEN)
