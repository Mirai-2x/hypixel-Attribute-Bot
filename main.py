url_auction = "https://api.hypixel.net/skyblock/auctions"
total_auctions = []

@bot.tree.command(name="at")
@app_commands.describe(armor="아이템 종류 선택", attribute="아트리부트 선택", level="레벨 선택")
@app_commands.choices(armor=armor_choices,attribute=attr_choices_list,level=get_level_choices)
async def at(interaction: discord.Interaction, armor: app_commands.Choice[str],attribute: app_commands.Choice[str],level: app_commands.Choice[str]):
    await interaction.response.defer() # 뒤로~ 미루기~
    selected_armor = armor.value  
    selected_attribute = attribute.value
    selected_level = level.value
    
    filtered_auctions, elapsed_time = await fetch_auctions(
        selected_armor, selected_attribute, selected_level)
    if filtered_auctions is None:
        embed = discord.Embed(description="데이터를 가져오는 데 실패했습니다.",
                              color=discord.Colour.red())
        await interaction.followup.send(embed=embed)
        return
    else:
        # 정상적으로 옥션 데이터를 찾은 경우 메시지 출력
        if len(filtered_auctions) == 0:
            embed = discord.Embed(description="조건에 맞는 아이템이 없습니다.",
                                  color=discord.Colour.red())
            await interaction.followup.send(embed=embed)
            return
        sorted_auctions = sorted(filtered_auctions,key=lambda x: x.get("starting_bid", 0))
        keywords = ["Crimson", "Terror", "Aurora", "Fervor", "Hollow"]
        top_5_auctions = sorted_auctions[:5]
        def create_auction_field(auction, selected_armor, selected_attribute,selected_level, keywords):
            item_name = auction.get("item_name")
            price = format_number(auction.get("starting_bid", 0))
            item_type = get_item_with_keywords(item_name, keywords)
            link = auction.get("uuid")
            emote = loaded_emotes.get(item_name,None) 

            if item_name == "Attribute Shard":
                field_name = f"{emote} Attribute Shard **({price})**" if emote else f"{item_type} {selected_armor} **({price})**"
            else:
                field_name = f"{emote} {item_type} {selected_armor} **({price})**" if emote else f"{item_type} {selected_armor} **({price})**"
            field_value = f"`/viewauction {link}`"
            return (field_name, field_value)

        top_5_auctions = sorted_auctions[:5]

        embed = discord.Embed(
            title="Attribute Finder",
            url="https://www.youtube.com/@%EC%A4%80%ED%9D%AC%EB%8B%98",
            description=
            f"**{selected_attribute}** **{selected_level}**을(를) 포함한 **{selected_armor}/Shard**\n**{len(filtered_auctions)}개**의 데이터({elapsed_time:.2f}초)\n",
            color=discord.Colour.red())

        for auction in top_5_auctions:
            field_name, field_value = create_auction_field(
                auction, selected_armor, selected_attribute, selected_level,
                keywords)

            embed.add_field(name=field_name, value=field_value, inline=False)
        embed.set_footer(text="준희님(slaylegit)")
        await interaction.followup.send(embed=embed)
        return

def get_item_with_keywords(item_name, keywords):
    item_name_lower = item_name.lower()
    found_keywords = [keyword for keyword in keywords if keyword.lower() in item_name_lower]
    return " ".join(found_keywords)

def filter_auctions(auctions, armor, attribute, level):
    keywords = ["Crimson", "Terror", "Aurora", "Fervor", "Hollow"]
    filtered_auctions = []
    print(armor, attribute, level)
    for auction in auctions:
        if auction.get("bin") and auction.get("item_name") == "Attribute Shard":
            lore = auction.get("item_lore")
            pattern = rf"{re.escape(attribute)} (I|II|III|IV|V|VI|VII|VIII|IX|X)"
            match = re.search(pattern, lore, re.IGNORECASE)
            if match:
                price = auction.get("starting_bid")
                matched_text = match.group(0)
                roman_part = matched_text.split()[-1]  #로마 숫자 split
                roman_value = roman_to_int(roman_part)
                if level == str(roman_value):
                    filtered_auctions.append(auction)
                    print(f"Attr: {matched_text}, '{roman_part}' is {roman_value}, Pr: {price}")
        if auction.get("bin") and auction.get("category") == "armor" and auction.get("tier","") == "LEGENDARY" and not auction.get("claimed", False):
            name = auction.get("item_name")
            lore = auction.get("item_lore")
            price = auction.get("starting_bid")
            if armor.lower() in name.lower() and any(
                    keyword.lower() in name.lower() for keyword in keywords):
                pattern = rf"{re.escape(attribute)} (I|II|III|IV|V|VI|VII|VIII|IX|X)"
                match = re.search(pattern, lore, re.IGNORECASE)
                if match:
                    matched_text = match.group(0)
                    roman_part = matched_text.split()[
                    roman_value = roman_to_int(roman_part)
                    if level == str(roman_value):
                        filtered_auctions.append(auction)
                        print(f"get: {name}, Text: {matched_text}, '{roman_part}' is {roman_value}, Pr: {price}")
    return filtered_auctions

def format_number(num):
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return str(num)

async def fetch_page(session, page):
    url = f"{url_auction}?page={page}"
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            return None

async def fetch_all_pages():
    async with aiohttp.ClientSession() as session:
        # get totalPages
        first_page_data = await fetch_page(session, 1)
        if first_page_data is None or 'totalPages' not in first_page_data:
            print("'totalPages' dosen't exits.")
            return None
        total_pages = first_page_data['totalPages']
        print(f"Total pages: {total_pages}")
        tasks = []
        for page in range(1, total_pages + 1):
            tasks.append(fetch_page(session, page))
        pages_data = await asyncio.gather(*tasks)
        return pages_data

async def fetch_auctions(armor, attribute, level):
    start_time = time.time()
    pages_data = await fetch_all_pages()
    if pages_data is not None:
        all_auctions = []
        for page_data in pages_data:
            if page_data:
                all_auctions.extend(page_data.get('auctions', []))  ### 옥션 데이터만 ###
        filtered_auctions = filter_auctions(all_auctions, armor, attribute,level)
        print(f"All Auctions: {len(all_auctions)}")
        print(f"Filtered Auctions: {len(filtered_auctions)}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        if not filtered_auctions:
            print("No auctions found after filtering.")
            return [], elapsed_time 
        return filtered_auctions, elapsed_time
    return [], None

def roman_to_int(roman):
    roman_numerals = {
        'I': 1,
        'II': 2,
        'III': 3,
        'IV': 4,
        'V': 5,
        'VI': 6,
        'VII': 7,
        'VIII': 8,
        'IX': 9,
        'X': 10
    }
    return roman_numerals.get(roman, 0)

class Level(BaseModel):
    name: str
    value: str

class Armor(BaseModel):
    name: str
    value: str

class Attribute(BaseModel):
    name: str
    value: str

class LevelChoices:
    def __init__(self) -> None:
        self.levels = []
    def addLevel(self, level: Level):
        self.levels.append(level)
    def getLevelChoices(self):
        return [
            app_commands.Choice(name=level.name, value=level.value)
            for level in self.levels
        ]

class AttrChoices:
    def __init__(self) -> None:
        self.attrs = []
    def addAttr(self, attr: Attribute):
        attr.name = attr.name[:25]
        self.attrs.append(attr)
    def getChoices(self):
        return [
            app_commands.Choice(name=attr.name,value=attr.value)
            for attr in self.attrs
        ]

level_choices = LevelChoices()
level_choices.addLevel(Level(name="1", value="1"))
level_choices.addLevel(Level(name="2", value="2"))
level_choices.addLevel(Level(name="3", value="3"))
level_choices.addLevel(Level(name="4", value="4"))
level_choices.addLevel(Level(name="5", value="5"))
level_choices.addLevel(Level(name="6", value="6"))
level_choices.addLevel(Level(name="7", value="7"))
level_choices.addLevel(Level(name="8", value="8"))
level_choices.addLevel(Level(name="9", value="9"))
level_choices.addLevel(Level(name="10", value="10"))
get_level_choices = level_choices.getLevelChoices()

attr_choices = AttrChoices()
attr_choices.addAttr(Attribute(name="Blazing Resistance", value="Blazing Resistance"))
attr_choices.addAttr(Attribute(name="Breeze", value="Breeze"))
attr_choices.addAttr(Attribute(name="Dominance", value="Dominance"))
attr_choices.addAttr(Attribute(name="Ender Resistance", value="Ender Resistance"))
attr_choices.addAttr(Attribute(name="Experience", value="Experience"))
attr_choices.addAttr(Attribute(name="Fortitude", value="Fortitude"))
attr_choices.addAttr(Attribute(name="Life Regeneration", value="Life Regeneration"))
attr_choices.addAttr(Attribute(name="Lifeline", value="Lifeline"))
attr_choices.addAttr(Attribute(name="Magic Find", value="Magic Find"))
attr_choices.addAttr(Attribute(name="Mana Pool", value="Mana Pool"))
attr_choices.addAttr(Attribute(name="Mana Regeneration", value="Mana Regeneration"))
attr_choices.addAttr(Attribute(name="Vitality", value="Vitality"))
attr_choices.addAttr(Attribute(name="Speed", value="Speed"))
attr_choices.addAttr(Attribute(name="Undead Resistance", value="Undead Resistance"))
attr_choices.addAttr(Attribute(name="Veteran", value="Veteran"))
attr_choices_list = attr_choices.getChoices()

class ArmorChoices:
    def __init__(self) -> None:
        self.armors = []
    def addArmor(self, armor: Armor):
        self.armors.append(armor)
    def getArmorChoices(self):
        return [
            app_commands.Choice(name=armor.name, value=armor.value)
            for armor in self.armors
        ]

armorChoices = ArmorChoices()
armorChoices.addArmor(Armor(name="Helmet", value="Helmet"))
armorChoices.addArmor(Armor(name="Chestplate", value="Chestplate"))
armorChoices.addArmor(Armor(name="Leggings", value="Leggings"))
armorChoices.addArmor(Armor(name="Boots", value="Boots"))
armor_choices = armorChoices.getArmorChoices()
