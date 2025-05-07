import disnake

from config import *
from db import TempVoices

class NameModal(disnake.ui.Modal):
    def __init__(self, arg) -> None:
        self.arg = arg
        components = [
            disnake.ui.TextInput(label="Название канала", placeholder="Введите новое название канала", custom_id="namemodal")
        ]

        super().__init__(title="Смена названия голосового канала", components=components, custom_id="namemodal")

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        name = interaction.text_values["namemodal"]
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        await channel.edit(name=name)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"Название голосового канала сменёно на **{name}**!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        return await interaction.response.send_message(embed=embed, ephemeral=True)

class LimitModal(disnake.ui.Modal):
    def __init__(self, arg) -> None:
        self.arg = arg
        components = [
            disnake.ui.TextInput(label="Лимит участников", placeholder="Введити новое число лимита участников", custom_id="limitmodal")
        ]

        super().__init__(title="Смена лимита участников войса", components=components, custom_id="limitmodalg")

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        limit = int(interaction.text_values["limitmodal"])
        if limit < 1 or limit > 99:
            return await interaction.response.send_message("Значение лимита должно находиться между 1 и 99!", ephemeral=True)
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        await channel.edit(user_limit=limit)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"Лимит личного голосового канала сменён на **{limit}**", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        return await interaction.response.send_message(embed=embed, ephemeral=True)

class KickSelect(disnake.ui.UserSelect):

    def __init__(self) -> None:
        super().__init__(
            placeholder="Выберите участника",
            min_values=1,
            max_values=1,
            custom_id="selectkick",
        )

    async def callback(self, interaction: disnake.MessageInteraction, /) -> None:
        player = self.values[0]
        voice_state = player.voice
        if not voice_state:
            return await interaction.response.send_message(
                "Выбранный участник не находится в голосовом канале.", ephemeral=True)
        channel = voice_state.channel
        prof_channel = await TempVoices.load(channel.id)
        if not prof_channel:
            return await interaction.response.send_message(
                "Выбранный участник находиться не в вашем голосовом канале.", ephemeral=True)
        if prof_channel.owner_id == player.id:
            return await interaction.response.send_message(
                "Вы не можете кикнуть владельца канала.", ephemeral=True)
        if player.voice and player.voice.channel.id != channel.id:
            return await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
        await player.move_to(None)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{player.mention} кикнут из вашей команты!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        return interaction.response.send_message(embed=embed, ephemeral=True)

class KickSelectView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(KickSelect())

class InviteSelectButton(disnake.ui.View):
    message: disnake.Message

    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player

    @disnake.ui.button(style=disnake.ButtonStyle.gray, label="От меня", custom_id="personally")
    async def personally(self, button: disnake.ui.Button, interaction):
        await interaction.response.defer()
        member = interaction.user
        voice_state = member.voice
        guild_name = interaction.guild.name
        voice_channel_link = await voice_state.channel.create_invite(max_age=86400)
        await self.player.send(f"🎉 **{member.name} приглашает вас в [голосовуху]({voice_channel_link}) в {guild_name}. Заходи быстрее >>**")
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True
        await interaction.message.edit(view=self)
        self.stop()
        embed = disnake.Embed(title="✅ Операция прошла успешно",
                              description=f"{self.player.name} отправлено приглашение в ваш голосовой канал!",
                              color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')
        await interaction.message.delete()
        await interaction.send(embed=embed)

    @disnake.ui.button(style=disnake.ButtonStyle.gray, label="Анонимно", custom_id="anonymously")
    async def anonymously(self, button: disnake.ui.Button, interaction):
        await interaction.response.defer()
        member = interaction.user
        voice_state = member.voice
        guild_name = interaction.guild.name
        voice_channel_link = await voice_state.channel.create_invite(max_age=86400)
        await self.player.send(f"🎉 **Вас пригласили в [голосовуху]({voice_channel_link}) в {guild_name}. Заходи быстрее >>**")
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True
        await interaction.message.edit(view=self)
        self.stop()
        embed = disnake.Embed(title="✅ Операция прошла успешно",
                              description=f"{self.player.name} отправлено приглашение в ваш голосовой канал!",
                              color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')
        await interaction.message.delete()
        await interaction.send(embed=embed)

class InviteSelect(disnake.ui.UserSelect):

    def __init__(self) -> None:
        super().__init__(
            placeholder="Выберите участника",
            min_values=1,
            max_values=1,
            custom_id="selectinvite",
        )

    async def callback(self, interaction: disnake.MessageInteraction, /) -> None:
        player = self.values[0]
        author = interaction.guild.get_member(interaction.author.id)
        channel = interaction.guild.get_channel(author.voice.channel.id)
        prof_channel = await TempVoices.load(author.voice.channel.id)
        if prof_channel.owner_id == player.id:
            return await interaction.response.send_message(
                "Вы не можете пригласить владельца канала.", ephemeral=True)
        view = InviteSelectButton(player)
        embed = disnake.Embed(title="❓ Вопрос", description="Отправить приглашение анонимно или от вашего лица?", color=0x2B2D31)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        message = await channel.send(embed=embed, view=view)
        return interaction.response.send_message(f"{author.mention} -> {message.jump_url}", ephemeral = True)

class InviteSelectView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(InviteSelect())

class AllowSelect(disnake.ui.UserSelect):

    def __init__(self) -> None:
        super().__init__(
            placeholder="Выберите участника",
            min_values=1,
            max_values=1,
            custom_id="selectallow",
        )

    async def callback(self, interaction: disnake.MessageInteraction, /) -> None:
        player = self.values[0]
        author = interaction.guild.get_member(interaction.author.id)
        channel = interaction.guild.get_channel(author.voice.channel.id)
        prof_channel = await TempVoices.load(channel.id)
        if prof_channel.owner_id == player.id:
            return await interaction.response.send_message("Вы не можете разрешить заходить владельцу канала.", ephemeral=True)
        await channel.set_permissions(player, connect=True)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{player.mention} теперь может подключаться к вашей комнате!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        return interaction.response.send_message(embed=embed, ephemeral=True)

class AllowSelectView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(AllowSelect())

class ForbidSelect(disnake.ui.UserSelect):

    def __init__(self) -> None:
        super().__init__(
            placeholder="Выберите участника",
            min_values=1,
            max_values=1,
            custom_id="selectforbid",
        )

    async def callback(self, interaction: disnake.MessageInteraction, /) -> None:
        player = self.values[0]
        author = interaction.guild.get_member(interaction.author.id)
        channel = interaction.guild.get_channel(author.voice.channel.id)
        prof_channel = await TempVoices.load(channel.id)
        if prof_channel and prof_channel.owner_id == player.id:
            return await interaction.response.send_message(
                "Вы не можете запретить входить владельцу канала.", ephemeral=True)
        await channel.set_permissions(player, connect=False)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{player.mention} больше не может подключаться к вашей комнате!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        return interaction.response.send_message(embed=embed, ephemeral=True)

class ForbidSelectView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(ForbidSelect())

class MuteSelect(disnake.ui.UserSelect):

    def __init__(self) -> None:
        super().__init__(
            placeholder="Выберите участника",
            min_values=1,
            max_values=1,
            custom_id="selectmute",
        )

    async def callback(self, interaction: disnake.MessageInteraction, /) -> None:
        player = self.values[0]
        voice_state = player.voice
        if not voice_state:
            return await interaction.response.send_message(
                "Выбранный участник не находится в голосовом канале.", ephemeral=True)
        channel = voice_state.channel
        prof_channel = await TempVoices.load(channel.id)
        if not prof_channel:
            return await interaction.response.send_message(
                "Выбранный участник находиться не в вашем голосовом канале.", ephemeral=True)
        if prof_channel.owner_id == player.id:
            return await interaction.response.send_message(
                "Вы не можете замутить владельца канала.", ephemeral=True)
        if player.voice and player.voice.channel.id != channel.id:
            return await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
        await player.edit(mute=True)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{player.mention} больше не может говорить в вашей комнате!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        return await interaction.response.send_message(embed=embed, ephemeral=True)

class MuteSelectView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(MuteSelect())

class HearSelect(disnake.ui.UserSelect):

    def __init__(self) -> None:
        super().__init__(
            placeholder="Выберите участника",
            min_values=1,
            max_values=1,
            custom_id="selecthear",
        )

    async def callback(self, interaction: disnake.MessageInteraction, /) -> None:
        player = self.values[0]
        voice_state = player.voice
        if not voice_state:
            return await interaction.response.send_message(
                "Выбранный участник не находится в голосовом канале.", ephemeral=True)
        channel = voice_state.channel
        prof_channel = await TempVoices.load(channel.id)
        if not prof_channel:
            return await interaction.response.send_message(
                "Выбранный участник находиться не в вашем голосовом канале.", ephemeral=True)
        if prof_channel.owner_id == player.id:
            return await interaction.response.send_message(
                "Вы не можете заглушить владельца канала.", ephemeral=True)
        if player.voice and player.voice.channel.id != channel.id:
            return await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
        await player.edit(deafen=True)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{player.mention} больше не может слушaть вашу комнату!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        return interaction.response.send_message(embed=embed, ephemeral=True)

class HearSelectView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(HearSelect())

class SelectSettings(disnake.ui.StringSelect):
    def __init__(self):
        super().__init__()
        options = [
            disnake.SelectOption(label="Сменить название", value="name", emoji=name_emoji),
            disnake.SelectOption(label="Изменить лимит", value="limit", emoji=limit_emoji),
            disnake.SelectOption(label="Кикнуть учасника", value="kick", emoji=kick_emoji),
            disnake.SelectOption(label="Пригласить учасника", value="invite", emoji=invite_emoji),
            disnake.SelectOption(label="Разрешить участника", value="allow", emoji=allow_emoji),
            disnake.SelectOption(label="Запретить участника", value="forbid", emoji=forbid_emoji),
            disnake.SelectOption(label="Замутить участника", value="mute", emoji=mute_emoji),
            disnake.SelectOption(label="Заглушить участника", value="hear", emoji=hear_emoji),
        ]

        super().__init__(
            placeholder="Выберите опцию",
            options=options,
            custom_id="selectsettings",
        )

class SelectSettingsView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(SelectSettings())