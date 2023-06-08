import disnake
from disnake.ext import commands
from disnake.utils import get
import json
import yaml


voice_file = 'voice.json'
config_file = 'config.yml'
try:
    with open(voice_file, 'r') as file:
        voice = json.load(file)
except FileNotFoundError:
    voice = {}

class NameModal(disnake.ui.Modal):
    def __init__(self, arg) -> None:
        self.arg = arg
        components = [
            disnake.ui.TextInput(label="Название канала", placeholder="Введите свое название канала", custom_id="namemodal")
        ]

        super().__init__(title="Смена названия голосового канала", components=components, custom_id="namemodalg")

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        name = interaction.text_values["namemodal"]
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        await channel.edit(name=name)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"Название голосового канала сменёно на {name}!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

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
            await interaction.response.send_message("Значение лимита должно находиться между 1 и 99!", ephemeral=True)
            return
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        await channel.edit(user_limit=limit)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"Лимит личного голосового канала сменён на {limit}", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

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
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете кикнуть владельца канала.", ephemeral=True)
            return
        if player.voice and player.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await player.move_to(None)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{player.mention} кикнут из вашей команты!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

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
        await self.player.send(f"🎉 {member.name} приглашает вас в голосовую команту в {guild_name}. Заходи быстрее >>\n {voice_channel_link}")
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
        await self.player.send(f"🎉 Вас пригласили в голосовую команту в {guild_name}. Заходи быстрее >>\n {voice_channel_link}")
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
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете пригласить владельца канала.", ephemeral=True)
            return
        if player.voice and player.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        view = InviteSelectButton(player)
        embed = disnake.Embed(title="❓ Вопрос", description="Отправить пришлашение анонимно или от вашего лица?", color=0x2B2D31)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed, view=view)

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
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете разрешить владельца канала.", ephemeral=True)
            return
        if player.voice and player.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await channel.set_permissions(player, connect=True)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description="Выбранный участник теперь может подключаться к вашей комнате!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

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
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете запретить владельца канала.", ephemeral=True)
            return
        if player.voice and player.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await channel.set_permissions(player, connect=False)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description="Выбранный участник больше не может подключаться к вашей комнате!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

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
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете замутить владельца канала.", ephemeral=True)
            return
        if player.voice and player.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await player.edit(mute=True)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description="Выбранный участник больше не может говорить в вашей комнате!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

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
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете заглушить владельца канала.", ephemeral=True)
            return
        if player.voice and player.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await player.edit(deafen=True)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description="Выбранный участник больше не может слушaть вашу комнату!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

class HearSelectView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(HearSelect())

class BitrateModal(disnake.ui.Modal):
    def __init__(self, arg) -> None:
        self.arg = arg
        components = [
            disnake.ui.TextInput(label="Введите нужное число", placeholder="От 8 до 384", custom_id="bitratemodal")
        ]

        super().__init__(title="Смена битрейта голосового канала", components=components, custom_id="bitratemodalg")

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        bitrate = int(interaction.text_values["bitratemodal"])
        if bitrate < 8000:
            await interaction.response.send_message("Значение битрейта должно быть не меньше 8000.", ephermal=True)
            return
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        await channel.edit(bitrate=bitrate)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"Битрейт личного голосового канала сменён на `{bitrate}`", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

class SelectSettings(disnake.ui.StringSelect):
    def __init__(self):
        super().__init__()
        options = [
            disnake.SelectOption(label="Сменить название", value="name", emoji="<:VoiceName:1113760036792057866>"),
            disnake.SelectOption(label="Изменить лимит", value="limit", emoji="<:VoiceLimit:1113773531470241822>"),
            disnake.SelectOption(label="Кикнуть учасника", value="kick", emoji="<:VoiceKick:1113772156589965352>"),
            disnake.SelectOption(label="Пригласить учасника", value="invite", emoji="<:VoiceInvite:1113780097833508866>"),
            disnake.SelectOption(label="Разрешить участника", value="allow", emoji="<:VoiceAllow:1113784060167323719>"),
            disnake.SelectOption(label="Запретить участника", value="forbid", emoji="<:VoiceDeny:1113783805606637658>"),
            disnake.SelectOption(label="Замутить участника", value="mute", emoji="<:VoiceMute:1113793201573220432>"),
            disnake.SelectOption(label="Заглушить участника", value="hear", emoji="<:VoiceHear:1113814627634130996>"),
            disnake.SelectOption(label="Изменить битрейт", value="bitrate", emoji="<:VoiceBiterate:1113778911042621571>"),
        ]

        super().__init__(
            placeholder="Выберите опцию",
            options=options,
            custom_id="selectsettings",
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        member = interaction.user
        voice_state = member.voice
        if voice_state is None or voice_state.channel is None or not isinstance(voice_state.channel,
                                                                                disnake.VoiceChannel):
            await interaction.response.send_message(
                "Вы должны находиться в голосовом канале для использования этой команды.", ephemeral=True)
            return
        channel = voice_state.channel
        if member.id not in voice or voice[member.id] != channel.id:
            await interaction.response.send_message(
                "Вы должны находиться в своем личном голосовом канале для управления панелью.", ephemeral=True)
            return
        if self.values[0] == "name":
            await interaction.response.send_modal(NameModal(self.values[0]))
        if self.values[0] == "limit":
            await interaction.response.send_modal(LimitModal(self.values[0]))
        if self.values[0] == "kick":
            view = KickSelectView()
            await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        if self.values[0] == "invite":
            view = InviteSelectView()
            await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        if self.values[0] == "allow":
            view = AllowSelectView()
            await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        if self.values[0] == "forbid":
            view = ForbidSelectView()
            await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        if self.values[0] == "mute":
            view = MuteSelectView()
            await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        if self.values[0] == "hear":
            view = HearSelectView()
            await interaction.response.send_message("Выберите участника ниже:", view=view, ephemeral=True)
        if self.values[0] == "bitrate":
            await interaction.response.send_modal(BitrateModal(self.values[0]))

class SelectSettingsView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(SelectSettings())

class Create(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistents_views_added = False

    @commands.Cog.listener('on_ready')
    async def on_ready(self):
        global voice
        try:
            with open(voice_file, 'r') as f:
                voice = json.load(f)
        except FileNotFoundError:
            voice = {}

    @commands.Cog.listener('on_voice_state_update')
    async def on_voice_state_update(self, member, before, after):
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        category_id = data['category_id']
        category = get(self.bot.get_all_channels(), id=category_id)
        channel_id = data['channel_id']
        global voice
        if after.channel and after.channel.id == channel_id:
            if member.id not in voice:
                voice_channel = await category.create_voice_channel(f'Канал {member.display_name}', bitrate=None)
                await voice_channel.set_permissions(member, priority_speaker=True)
                await member.move_to(voice_channel)
                await voice_channel.send("Добро пожаловать в свой личный войс!")
                voice[member.id] = voice_channel.id
                save_voice()
        elif before.channel and member.id in voice and before.channel.id == voice[member.id] and not before.channel.members:
            await before.channel.delete()
            del voice[member.id]
            save_voice()
        elif before.channel and before.channel.id in voice and not before.channel.members and len(before.channel.members) == 0:
            await before.channel.delete()
            del voice[member.id]
            save_voice()
        else:
            pass

    @commands.slash_command(name="setup", description="Устанавливает меню управления комнатами")
    async def setup(self, ctx):
        view = SelectSettingsView()
        embed1 = disnake.Embed(color=0x2B2D31)
        embed1.set_image(url="https://cdn.discordapp.com/attachments/1087624157333819452/1113836305554616433/interfeis.png")
        embed2 = disnake.Embed(title="", description=
                                f"###  <:VoiceName:1113760036792057866> - Изменить название вашей комнаты\n"
                                f"###  <:VoiceLimit:1113773531470241822> - Изменить лимит вашей комнаты\n"
                                f"###  <:VoiceKick:1113772156589965352> - Кикнуть участника из вашей команты\n"
                                f"###  <:VoiceInvite:1113780097833508866> - Пригласить участника\n"
                                f"###  <:VoiceAllow:1113784060167323719> - Разрешить участника\n"
                                f"###  <:VoiceDeny:1113783805606637658> - Запретить участника\n"
                                f"###  <:VoiceMute:1113793201573220432> - За/РазМутить участника\n"
                                f"###  <:VoiceHear:1113814627634130996> - За/РазГлушить участника\n"
                                f"###  <:VoiceBiterate:1113778911042621571> - Изменить битрейт вашей команты", color=0x2B2D31)
        embed2.set_image(url='https://imgur.com/GpL91Zm')
        await ctx.channel.send(embeds=[embed1, embed2], view=view)

    @commands.Cog.listener()
    async def on_connect(self):
        if self.persistents_views_added:
            return

        self.bot.add_view(SelectSettingsView())
        self.persistents_views_added = True

    @commands.slash_command()
    async def voice(self, interaction):
        member = interaction.user
        voice_state = member.voice
        if voice_state is None or voice_state.channel is None or not isinstance(voice_state.channel,
                                                                                disnake.VoiceChannel):
            await interaction.response.send_message(
                "Вы должны находиться в голосовом канале для использования этой команды.", ephemeral=True)
            return
        channel = voice_state.channel
        if member.id not in voice or voice[member.id] != channel.id:
            await interaction.response.send_message(
                "Вы должны находиться в своем личном голосовом канале для управления панелью.", ephemeral=True)
            return
        pass

    @voice.sub_command(description="Изменить лимит голосового канала")
    async def limit(self, interaction, limit: int = commands.Param(name="лимит")):
        global voice
        if limit < 1 or limit > 99:
            await interaction.response.send_message("Значение лимита должно находиться между `1` и `99`!", ephemeral=True)
            return
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        await channel.edit(user_limit=limit)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"Лимит личного голосового канала сменён на `{limit}`", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.send(embed=embed)

    @voice.sub_command(description="Изменить название голосового канала")
    async def name(self, interaction, name: str = commands.Param(name="название")):
        if len(name) < 1 or len(name) > 100:
            await interaction.response.send_message("Количество символов в названии должно находиться между `1` и `100`!", ephemeral=True)
            return
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        await channel.edit(name=name)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"Название личного голосового канала сменёно на `{name}`", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @voice.sub_command(description="Кикнуть участника из гч")
    async def kick(self, interaction, user: disnake.Member = commands.Param(name="участник")):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id not in voice or voice.get(member.id) != channel.id:
            await interaction.response.send_message(
                "Вы не можете кикнуть владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await user.move_to(None)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{user.mention} кикнут из вашей команты!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @voice.sub_command(description="Пригласить участника")
    async def invite(self, interaction, user: disnake.Member = commands.Param(name="участник")):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id not in voice or voice.get(member.id) != channel.id:
            await interaction.response.send_message(
                "Вы не можете пригласить владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        player = user
        view = InviteSelectButton(player)
        embed = disnake.Embed(title="❓ Вопрос", description="Отправить пришлашение анонимно или от вашего лица?", color=0x2B2D31)
        embed.set_footer(text="! Приглашение отсылается в лс !")
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed, view=view)

    @voice.sub_command(description="Разрешить участника")
    async def allow(self, interaction, user: disnake.Member = commands.Param(name="участник")):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id not in voice or voice.get(member.id) != channel.id:
            await interaction.response.send_message(
                "Вы не можете разрешить владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await channel.set_permissions(user, connect=True)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{user.mention} теперь может подключаться к вашей комнате!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @voice.sub_command(description="Запретить участника")
    async def forbid(self, interaction, user: disnake.Member = commands.Param(name="участник")):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id not in voice or voice.get(member.id) != channel.id:
            await interaction.response.send_message(
                "Вы не можете запретить владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await channel.set_permissions(user, connect=False)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{user.mention} больше не может подключаться к вашей комнате!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @voice.sub_command(description="Замутить участника")
    async def mute(self, interaction, user: disnake.Member = commands.Param(name="участник")):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете замутить владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await user.edit(mute=True)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{user.mention} больше не может говорить в вашей комнате!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @voice.sub_command(description="Размутить участника")
    async def unmute(self, interaction, user: disnake.Member = commands.Param(name="участник")):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете замутить владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await user.edit(mute=False)

        embed = disnake.Embed(title="✅ Операция прошла успешно",
                              description=f"{user.mention} теперь может говорить в вашей комнате!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @voice.sub_command(description="Заглушить участника")
    async def hear(self, interaction, user: disnake.Member = commands.Param(name="участник")):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете заглушить владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await user.edit(deafen=True)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{user.mention} больше не может слушaть вашу комнату!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @voice.sub_command(description="Разглушить участника")
    async def unhear(self, interaction, user: disnake.Member = commands.Param(name="участник")):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете заглушить владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await user.edit(deafen=False)

        embed = disnake.Embed(title="✅ Операция прошла успешно",
                              description=f"{user.mention} теперь может слушaть вашу комнату!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @voice.sub_command(description="Изменить битрейт")
    async def bitrate(self, interaction, bitrate: int = commands.Param(name="число")):
        if bitrate < 8000:
            await interaction.response.send_message("Значение битрейта должно быть не меньше 8000.", ephermal=True)
            return
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        await channel.edit(bitrate=bitrate)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"Битрейт личного голосового канала сменён на `{bitrate}`", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="voices")
    async def voices(self, interaction):
        pass

    @voices.sub_command(description="Показывает информацию о канале")
    async def info(self, interaction, channel: disnake.VoiceChannel):
        voice_channel = channel
        member_count = len(voice_channel.members)
        channel_name = voice_channel.name
        channel_limit = voice_channel.user_limit
        if channel_limit == 0:
             channel_limit = "∞"
        channel_bitrate = voice_channel.bitrate

        embed = disnake.Embed(title="Информация о канале", color=0x6b9bba)
        embed.add_field(name="Название:", value=f"{channel_name}", inline=False)
        embed.add_field(name="Количество:", value=f"{str(member_count)} участников", inline=False)
        embed.add_field(name="Лимит:", value=str(channel_limit), inline=False)
        embed.add_field(name="Битрейт:", value=str(channel_bitrate), inline=False)

        await interaction.response.send_message(embed=embed)

    @commands.user_command(name="Кикнуть из войса")
    async def userkick(self, interaction, user: disnake.Member):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id not in voice or voice.get(member.id) != channel.id:
            await interaction.response.send_message(
                "Вы не можете кикнуть владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        await user.move_to(None)

        embed = disnake.Embed(title="✅ Операция прошла успешно", description=f"{user.mention} кикнут из вашей команты!",
                              color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @commands.user_command(name="Пригласить в войс")
    async def userinvite(self, interaction, user: disnake.Member):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id not in voice or voice.get(member.id) != channel.id:
            await interaction.response.send_message(
                "Вы не можете пригласить владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        player = user
        view = InviteSelectButton(player)
        embed = disnake.Embed(title="❓ Вопрос", description="Отправить пришлашение анонимно или от вашего лица?", color=0x2B2D31)
        embed.set_footer(text="! Приглашение отсылается в лс !")
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed, view=view)

    @commands.user_command(name="Разрешить/Запретить подключение")
    async def userallow(self, interaction, user: disnake.Member):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id not in voice or voice.get(member.id) != channel.id:
            await interaction.response.send_message(
                "Вы не можете разрешить владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        if user.permissions_in(channel).connect:
            await channel.set_permissions(user, connect=False)
            embed = disnake.Embed(title="✅ Операция прошла успешно",
                                  description=f"{user.mention} больше не может подключаться к вашей комнате!",
                                  color=0x6b9bba)
        else:
            await channel.set_permissions(user, connect=True)
            embed = disnake.Embed(title="✅ Операция прошла успешно",
                                  description=f"{user.mention} теперь может подключаться к вашей комнате!",
                                  color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @commands.user_command(name="Замутить/Размутить в войсе")
    async def usermute(self, interaction, user: disnake.Member):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете замутить владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        if user.voice.mute:
            await user.edit(mute=False)
            embed = disnake.Embed(title="✅ Операция прошла успешно",
                                  description=f"{user.mention} теперь может слушать вашу комнату!", color=0x6b9bba)
        else:
            await user.edit(mute=True)
            embed = disnake.Embed(title="✅ Операция прошла успешно",
                                  description=f"{user.mention} больше не может слушать вашу комнату!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

    @commands.user_command(name="Заглушить/Разглушить в войсе")
    async def userhear(self, interaction, user: disnake.Member):
        member = interaction.user
        voice_state = member.voice
        channel = voice_state.channel
        if not voice_state or not voice_state.channel:
            await interaction.response.send_message(
                "Выбранный участник не находится в вашем голосовом канале.", ephemeral=True)
            return
        if member.id in voice or voice[member.id] == channel.id:
            await interaction.response.send_message(
                "Вы не можете заглушить владельца канала.", ephemeral=True)
            return
        if user.voice and user.voice.channel.id != channel.id:
            await interaction.response.send_message(
                "Выбранный участник находится в другом голосовом канале.", ephemeral=True)
            return
        if user.voice.deaf:
            await user.edit(deafen=False)
            embed = disnake.Embed(title="✅ Операция прошла успешно",
                                  description=f"{user.mention} теперь может слушать вашу комнату!", color=0x6b9bba)
        else:
            await user.edit(deafen=True)
            embed = disnake.Embed(title="✅ Операция прошла успешно",
                                  description=f"{user.mention} больше не может слушать вашу комнату!", color=0x6b9bba)
        embed.set_image(url='https://imgur.com/GpL91Zm')

        await interaction.response.send_message(embed=embed)

def save_voice():
    with open(voice_file, 'w') as file:
        json.dump(voice, file)

def setup(bot):
    bot.add_cog(Create(bot))