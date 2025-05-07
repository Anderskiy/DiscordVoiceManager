from disnake.ext import commands
from random import choice

from utils import *
from config import *

command_sync_flags = commands.CommandSyncFlags.all()

bot = commands.Bot(command_prefix=".", help_command=None, intents=disnake.Intents.all(),
                   command_sync_flags=command_sync_flags)


@bot.slash_command(name="setup_temp", description="Установить интерфейс для временных каналов", dm_permission=False)
async def setup_temp_menu(interaction):
    view = SelectSettingsView()
    embed = disnake.Embed(title="", description=
    f"# ⚙️ Настройка временных комнат\n"
    f"###  <:VoiceName:1113760036792057866> - Изменить название вашей комнаты\n"
    f"###  <:VoiceLimit:1113773531470241822> - Изменить лимит вашей комнаты\n"
    f"###  <:VoiceKick:1113772156589965352> - Кикнуть участника из вашей команты\n"
    f"###  <:VoiceInvite:1113780097833508866> - Пригласить участника\n"
    f"###  <:VoiceAllow:1113784060167323719> - Разрешить участника\n"
    f"###  <:VoiceDeny:1113783805606637658> - Запретить участника\n"
    f"###  <:VoiceMute:1113793201573220432> - За/РазМутить участника\n"
    f"###  <:VoiceHear:1113814627634130996> - За/РазГлушить участника\n", color=0x2B2D31)
    embed.set_image(url='https://imgur.com/GpL91Zm')
    await interaction.channel.send(embed=embed, view=view)


@bot.event
async def on_voice_state_update(member, before, after):
    category = disnake.utils.get(bot.get_all_channels(), id=category_channel_id)
    if before.channel:
        owner_channel = await TempVoices.load_by_owner(member.id)
        if owner_channel and owner_channel.channel_id == before.channel.id:
            if not before.channel.members:
                await before.channel.delete()
                await TempVoices.voice_delete(before.channel.id)
            elif len(before.channel.members) >= 1:
                new_owner = choice(before.channel.members)
                await TempVoices.give_owner(before.channel.id, new_owner.id)

    elif after.channel:
        if not before.channel and after.channel.id == create_channel_id:
            voice_channel = await category.create_voice_channel(f'Канал {member.display_name}', bitrate=None)
            await voice_channel.set_permissions(member, priority_speaker=True)
            await member.move_to(voice_channel)
            await voice_channel.send("Добро пожаловать в свой личный войс!")
            await TempVoices.voice_create(after.channel.id, member.id)


@bot.event
async def on_dropdown(interaction: disnake.MessageInteraction):
    if interaction.data.custom_id != "selectsettings": return None
    voice_state = interaction.user.voice
    if not voice_state or not voice_state.channel or not isinstance(voice_state.channel, disnake.VoiceChannel):
        return await interaction.response.send_message(
            "Вы должны находиться в голосовом канале для использования этого меню.", ephemeral=True)
    owner_channel = await TempVoices.load_by_owner(interaction.author.id)
    if not owner_channel:
        return await interaction.response.send_message(
            "Вы должны находиться в своем личном голосовом канале для управления панелью.", ephemeral=True)
    match interaction.values:
        case ["name"]:
            return await interaction.response.send_modal(NameModal(interaction.values))
        case ["limit"]:
            return await interaction.response.send_modal(NameModal(interaction.values))
        case ["kick"]:
            view = KickSelectView()
            return await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        case ["invite"]:
            view = InviteSelectView()
            return await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        case ["allow"]:
            view = AllowSelectView()
            return await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        case ["forbid"]:
            view = ForbidSelectView()
            return await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        case ["mute"]:
            view = MuteSelectView()
            return await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        case ["hear"]:
            view = HearSelectView()
            return await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        case _:
            return None


if __name__ == "__main__":
    bot.run(TOKEN)
