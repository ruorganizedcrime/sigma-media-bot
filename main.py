# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import hbold, hitalic, hcode
import config
import database as db
import keyboards as kb

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(storage=MemoryStorage())

ADMIN_ID = config.ADMIN_IDS[0]

class MovieUpload(StatesGroup):
    title = State()
    description = State()
    year = State()
    genre = State()
    imdb = State()
    thumbnail = State()
    video = State()

class SeriesUpload(StatesGroup):
    title = State()
    description = State()
    year = State()
    genre = State()
    imdb = State()
    thumbnail = State()
    total_seasons = State()
    current_season = State()
    current_episode = State()
    episode_title = State()
    episode_thumbnail = State()
    episode_video = State()

def get_type_emoji(media_type: str) -> str:
    emojis = {
        'movie': '🎬',
        'series': '📺',
        'anime_movie': '🍥',
        'anime_series': '🍥'
    }
    return emojis.get(media_type, '📹')

def get_type_name(media_type: str) -> str:
    names = {
        'movie': 'Фильм',
        'series': 'Сериал',
        'anime_movie': 'Аниме-фильм',
        'anime_series': 'Аниме-сериал'
    }
    return names.get(media_type, media_type)

async def get_admin_username() -> str:
    try:
        user = await bot.get_chat(ADMIN_ID)
        return user.username or f"ID {ADMIN_ID}"
    except:
        return f"ID {ADMIN_ID}"

def get_sigma_info_text() -> str:
    return (
        "👑 <b>КТО ТАКОЙ СИГМА?</b> 👑\n\n"
        
        "🔹 <b>Определение:</b>\n"
        "Сигма (Sigma) — это архетип мужчины, который стоит вне иерархии. "
        "В отличие от альф, которые стремятся к лидерству, и бет, которые ищут "
        "принадлежности к группе, сигма — одиночка, который не нуждается в "
        "одобрении общества.\n\n"
        
        "🔹 <b>Ключевые черты Сигмы:</b>\n\n"
        
        "▫️ <b>Независимость</b> — не следует за толпой, сам выбирает свой путь\n"
        "▫️ <b>Интровертность</b> — комфортно чувствует себя в одиночестве\n"
        "▫️ <b>Загадочность</b> — никогда не раскрывает все карты\n"
        "▫️ <b>Уверенность</b> — не нуждается в подтверждении своей ценности\n"
        "▫️ <b>Избирательность</b> — тщательно выбирает круг общения\n"
        "▫️ <b>Наблюдательность</b> — больше слушает, чем говорит\n"
        "▫️ <b>Адаптивность</b> — может быть как альфой, так и бетой, когда нужно\n\n"
        
        "🔹 <b>Как ведут себя Сигмы:</b>\n\n"
        "🏔️ <b>В обществе:</b> Держатся в тени, но когда говорят — их слушают. "
        "Не участвуют в стадных инстинктах и массовых движениях.\n\n"
        
        "💼 <b>В работе:</b> Часто выбирают фриланс или предпринимательство. "
        "Не терпят жесткой иерархии и начальников над собой.\n\n"
        
        "❤️ <b>В отношениях:</b> Ценят личное пространство. Не терпят токсичных "
        "людей и эмоциональных качелей. Партнер должен быть самостоятельной личностью.\n\n"
        
        "🧠 <b>В развитии:</b> Постоянно самосовершенствуются. Читают, учатся новому, "
        "работают над телом и духом. Инвестируют в себя, а не в показную роскошь.\n\n"
        
        "🔹 <b>Цитата, описывающая Сигму:</b>\n"
        "<i>«Волк-одиночка не ищет стаю, потому что он сам себе стая»</i>\n\n"
        
        "⚡ <b>Sigma Media — контент для тех, кто мыслит независимо!</b> ⚡"
    )

async def send_or_edit_message(callback: CallbackQuery, text: str, reply_markup=None, parse_mode=None, photo=None):
    try:
        if callback.inline_message_id:
            if photo:
                await bot.send_photo(
                    chat_id=callback.from_user.id,
                    photo=photo,
                    caption=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
            else:
                await bot.edit_message_text(
                    inline_message_id=callback.inline_message_id,
                    text=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
        else:
            if photo:
                if callback.message:
                    await callback.message.delete()
                await bot.send_photo(
                    chat_id=callback.message.chat.id,
                    photo=photo,
                    caption=text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
            else:
                await callback.message.edit_text(
                    text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
    except Exception as e:
        logging.error(f"Error in send_or_edit_message: {e}")
        if photo:
            await bot.send_photo(
                chat_id=callback.from_user.id if callback.inline_message_id else callback.message.chat.id,
                photo=photo,
                caption=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        else:
            await bot.send_message(
                chat_id=callback.from_user.id if callback.inline_message_id else callback.message.chat.id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_name = message.from_user.first_name
    admin_username = await get_admin_username()
    
    text = (
        f"👋 Привет, {user_name}!\n\n"
        f"Добро пожаловать в {config.BOT_NAME}!\n\n"
        f"🔍 Как искать фильмы:\n"
        f"В этом чате напишите {config.BOT_USERNAME} и название фильма\n\n"
        f"👨‍💻 Разработчик: @{admin_username}"
    )
    
    await message.answer(
        text,
        reply_markup=kb.get_start_inline_keyboard()
    )
    
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer(
            "Панель администратора:",
            reply_markup=kb.get_admin_keyboard()
        )

@dp.callback_query(F.data == "sigma_info")
async def show_sigma_info(callback: CallbackQuery):
    await callback.answer()
    
    sigma_text = get_sigma_info_text()
    
    await send_or_edit_message(
        callback,
        sigma_text,
        parse_mode="HTML",
        reply_markup=kb.get_sigma_info_keyboard()
    )

@dp.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    await callback.answer()
    
    user_name = callback.from_user.first_name
    admin_username = await get_admin_username()
    
    text = (
        f"👋 Привет, {user_name}!\n\n"
        f"Добро пожаловать в {config.BOT_NAME}!\n\n"
        f"🔍 Как искать фильмы:\n"
        f"В этом чате напишите {config.BOT_USERNAME} и название фильма\n\n"
        f"👨‍💻 Разработчик: @{admin_username}"
    )
    
    await send_or_edit_message(
        callback,
        text,
        parse_mode="HTML",
        reply_markup=kb.get_start_inline_keyboard()
    )

@dp.inline_query()
async def inline_search(query: InlineQuery):
    search_query = query.query or ""
    
    results = db.fuzzy_search_media(search_query, limit=20)
    
    inline_results = []
    
    for media in results:
        emoji = get_type_emoji(media['type'])
        title = media['title']
        year = media['year']
        
        result_text = f"{emoji} {title}"
        if year:
            result_text += f" ({year})"
        
        type_name = get_type_name(media['type'])
        
        description_preview = media['description'][:200] + "..." if media['description'] and len(media['description']) > 200 else media['description']
        
        full_text = (
            f"{emoji} {hbold(title)}\n\n"
            f"📋 Тип: {type_name}\n"
            f"📅 Год: {media['year']}\n"
            f"🎭 Жанр: {media['genre']}\n"
        )
        
        if media['imdb']:
            full_text += f"⭐ IMDb: {media['imdb']:.1f}\n"
        
        full_text += f"\n📝 {description_preview}"
        
        inline_results.append(
            InlineQueryResultArticle(
                id=str(media['id']),
                title=result_text,
                description=f"{media['genre']} | {type_name}",
                input_message_content=InputTextMessageContent(
                    message_text=full_text,
                    parse_mode="HTML"
                ),
                reply_markup=kb.get_media_action_keyboard(media['id'])
            )
        )
    
    await query.answer(inline_results, cache_time=5, is_personal=True)

@dp.callback_query(F.data.startswith("watch_"))
async def watch_media(callback: CallbackQuery):
    media_id = int(callback.data.split("_")[1])
    media = db.get_media_by_id(media_id)
    
    if not media:
        await callback.answer("Контент не найден!", show_alert=True)
        return
    
    await callback.answer()
    
    if media['type'] in ['movie', 'anime_movie']:
        episodes = db.get_episodes_by_media(media_id)
        if episodes:
            chat_id = callback.from_user.id if callback.inline_message_id else callback.message.chat.id
            await bot.send_video(
                chat_id=chat_id,
                video=episodes[0]['file_id'],
                caption=f"{get_type_emoji(media['type'])} {hbold(media['title'])}",
                parse_mode="HTML"
            )
        else:
            await callback.answer("Видео не найдено!", show_alert=True)
    
    elif media['type'] in ['series', 'anime_series']:
        await send_or_edit_message(
            callback,
            f"{get_type_emoji(media['type'])} {hbold(media['title'])}\n\n"
            f"Выберите сезон:",
            parse_mode="HTML",
            reply_markup=kb.get_seasons_keyboard(media_id, media['total_seasons'])
        )

@dp.callback_query(F.data.startswith("info_"))
async def info_media(callback: CallbackQuery):
    media_id = int(callback.data.split("_")[1])
    media = db.get_media_by_id(media_id)
    
    if not media:
        await callback.answer("Контент не найден!", show_alert=True)
        return
    
    await callback.answer()
    
    type_name = get_type_name(media['type'])
    emoji = get_type_emoji(media['type'])
    
    text = (
        f"{emoji} {hbold(media['title'])}\n\n"
        f"📋 Тип: {type_name}\n"
        f"📅 Год: {media['year']}\n"
        f"🎭 Жанр: {media['genre']}\n"
    )
    
    if media['imdb']:
        text += f"⭐ IMDb: {media['imdb']:.1f}\n"
    
    text += f"📅 Добавлено: {media['upload_date'][:10]}\n"
    text += f"🔢 ID: {media['id']}\n\n"
    text += f"📝 {media['description']}"
    
    await send_or_edit_message(
        callback,
        text,
        parse_mode="HTML",
        reply_markup=kb.get_media_action_keyboard(media_id),
        photo=media.get('thumbnail')
    )

@dp.callback_query(F.data.startswith("season_"))
async def show_season(callback: CallbackQuery):
    _, media_id, season = callback.data.split("_")
    media_id = int(media_id)
    season = int(season)
    
    episodes = db.get_episodes_by_season(media_id, season)
    
    if not episodes:
        await callback.answer("В этом сезоне нет серий", show_alert=True)
        return
    
    await callback.answer()
    
    await send_or_edit_message(
        callback,
        f"Сезон {season} - выберите серию:",
        reply_markup=kb.get_episodes_keyboard(media_id, season, episodes)
    )

@dp.callback_query(F.data.startswith("seasons_"))
async def show_seasons(callback: CallbackQuery):
    media_id = int(callback.data.split("_")[1])
    media = db.get_media_by_id(media_id)
    
    await callback.answer()
    
    await send_or_edit_message(
        callback,
        f"{get_type_emoji(media['type'])} {hbold(media['title'])}\n\n"
        f"Выберите сезон:",
        parse_mode="HTML",
        reply_markup=kb.get_seasons_keyboard(media_id, media['total_seasons'])
    )

@dp.callback_query(F.data.startswith("episode_"))
async def show_episode(callback: CallbackQuery):
    _, media_id, season, episode = callback.data.split("_")
    media_id = int(media_id)
    season = int(season)
    episode = int(episode)
    
    episode_data = db.get_episode(media_id, season, episode)
    media = db.get_media_by_id(media_id)
    
    if not episode_data:
        await callback.answer("Серия не найдена!", show_alert=True)
        return
    
    await callback.answer()
    
    caption = f"{get_type_emoji(media['type'])} {hbold(media['title'])} - Сезон {season}, Серия {episode}"
    if episode_data['title']:
        caption += f"\n{hitalic(episode_data['title'])}"
    
    chat_id = callback.from_user.id if callback.inline_message_id else callback.message.chat.id
    await bot.send_video(
        chat_id=chat_id,
        video=episode_data['file_id'],
        caption=caption,
        parse_mode="HTML"
    )

@dp.message(F.text == "📤 Загрузить фильм")
async def upload_movie_start(message: Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    await state.update_data(type="movie")
    await state.set_state(MovieUpload.title)
    await message.answer("Введите название фильма:")

@dp.message(F.text == "🍥 Загрузить аниме фильм")
async def upload_anime_movie_start(message: Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    await state.update_data(type="anime_movie")
    await state.set_state(MovieUpload.title)
    await message.answer("Введите название аниме-фильма:")

@dp.message(MovieUpload.title)
async def upload_movie_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(MovieUpload.description)
    await message.answer("Введите описание:")

@dp.message(MovieUpload.description)
async def upload_movie_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(MovieUpload.year)
    await message.answer("Введите год выпуска:")

@dp.message(MovieUpload.year)
async def upload_movie_year(message: Message, state: FSMContext):
    try:
        year = int(message.text)
        await state.update_data(year=year)
        await state.set_state(MovieUpload.genre)
        await message.answer("Введите жанр (через запятую):")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный год (число):")

@dp.message(MovieUpload.genre)
async def upload_movie_genre(message: Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await state.set_state(MovieUpload.imdb)
    await message.answer("Введите рейтинг IMDb (или /skip чтобы пропустить):")

@dp.message(MovieUpload.imdb)
async def upload_movie_imdb(message: Message, state: FSMContext):
    if message.text.lower() == "/skip":
        await state.update_data(imdb=None)
    else:
        try:
            imdb = float(message.text.replace(',', '.'))
            if 0 <= imdb <= 10:
                await state.update_data(imdb=imdb)
            else:
                await message.answer("Рейтинг должен быть от 0 до 10. Попробуйте еще раз или /skip:")
                return
        except ValueError:
            await message.answer("Пожалуйста, введите число или /skip:")
            return
    
    await state.set_state(MovieUpload.thumbnail)
    await message.answer("Отправьте обложку (фото) или /skip чтобы пропустить:")

@dp.message(MovieUpload.thumbnail, F.photo)
async def upload_movie_thumbnail(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(thumbnail=file_id)
    await state.set_state(MovieUpload.video)
    await message.answer("Отправьте видеофайл:")

@dp.message(MovieUpload.thumbnail, F.text == "/skip")
async def skip_movie_thumbnail(message: Message, state: FSMContext):
    await state.update_data(thumbnail=None)
    await state.set_state(MovieUpload.video)
    await message.answer("Отправьте видеофайл:")

@dp.message(MovieUpload.video, F.video)
async def upload_movie_video(message: Message, state: FSMContext):
    data = await state.get_data()
    
    media_type = data.get('type', 'movie')
    
    media_id = db.add_media(
        title=data['title'],
        description=data['description'],
        year=data['year'],
        genre=data['genre'],
        type=media_type,
        total_seasons=1,
        uploaded_by=message.from_user.id,
        imdb=data.get('imdb'),
        thumbnail=data.get('thumbnail')
    )
    
    db.add_episode(
        media_id=media_id,
        season_number=1,
        episode_number=1,
        file_id=message.video.file_id,
        title=None,
        duration=message.video.duration
    )
    
    db.update_media_episodes_count(media_id, 1)
    
    await message.answer(
        f"✅ Фильм успешно загружен!\n"
        f"ID: {media_id}\n"
        f"Название: {data['title']}"
    )
    await state.clear()

@dp.message(F.text == "📤 Загрузить сериал")
async def upload_series_start(message: Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    await state.update_data(type="series")
    await state.set_state(SeriesUpload.title)
    await message.answer("Введите название сериала:")

@dp.message(F.text == "🍥 Загрузить аниме сериал")
async def upload_anime_series_start(message: Message, state: FSMContext):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    await state.update_data(type="anime_series")
    await state.set_state(SeriesUpload.title)
    await message.answer("Введите название аниме-сериала:")

@dp.message(SeriesUpload.title)
async def upload_series_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(SeriesUpload.description)
    await message.answer("Введите описание:")

@dp.message(SeriesUpload.description)
async def upload_series_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(SeriesUpload.year)
    await message.answer("Введите год выпуска:")

@dp.message(SeriesUpload.year)
async def upload_series_year(message: Message, state: FSMContext):
    try:
        year = int(message.text)
        await state.update_data(year=year)
        await state.set_state(SeriesUpload.genre)
        await message.answer("Введите жанр (через запятую):")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный год (число):")

@dp.message(SeriesUpload.genre)
async def upload_series_genre(message: Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await state.set_state(SeriesUpload.imdb)
    await message.answer("Введите рейтинг IMDb (или /skip чтобы пропустить):")

@dp.message(SeriesUpload.imdb)
async def upload_series_imdb(message: Message, state: FSMContext):
    if message.text.lower() == "/skip":
        await state.update_data(imdb=None)
    else:
        try:
            imdb = float(message.text.replace(',', '.'))
            if 0 <= imdb <= 10:
                await state.update_data(imdb=imdb)
            else:
                await message.answer("Рейтинг должен быть от 0 до 10. Попробуйте еще раз или /skip:")
                return
        except ValueError:
            await message.answer("Пожалуйста, введите число или /skip:")
            return
    
    await state.set_state(SeriesUpload.thumbnail)
    await message.answer("Отправьте обложку сериала (фото) или /skip чтобы пропустить:")

@dp.message(SeriesUpload.thumbnail, F.photo)
async def upload_series_thumbnail(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(thumbnail=file_id)
    await state.set_state(SeriesUpload.total_seasons)
    await message.answer("Введите количество сезонов:")

@dp.message(SeriesUpload.thumbnail, F.text == "/skip")
async def skip_series_thumbnail(message: Message, state: FSMContext):
    await state.update_data(thumbnail=None)
    await state.set_state(SeriesUpload.total_seasons)
    await message.answer("Введите количество сезонов:")

@dp.message(SeriesUpload.total_seasons)
async def upload_series_seasons(message: Message, state: FSMContext):
    try:
        total_seasons = int(message.text)
        await state.update_data(total_seasons=total_seasons)
        await state.update_data(current_season=1)
        
        data = await state.get_data()
        media_id = db.add_media(
            title=data['title'],
            description=data['description'],
            year=data['year'],
            genre=data['genre'],
            type=data['type'],
            total_seasons=total_seasons,
            uploaded_by=message.from_user.id,
            imdb=data.get('imdb'),
            thumbnail=data.get('thumbnail')
        )
        
        await state.update_data(media_id=media_id)
        await state.update_data(episode_count=0)
        await state.set_state(SeriesUpload.current_episode)
        
        await message.answer(f"Сезон 1 из {total_seasons}")
        await message.answer(f"Введите количество серий в 1 сезоне:")
        
    except ValueError:
        await message.answer("Пожалуйста, введите число:")

@dp.message(SeriesUpload.current_episode)
async def upload_season_episodes(message: Message, state: FSMContext):
    try:
        episodes_in_season = int(message.text)
        data = await state.get_data()
        
        current_season = data['current_season']
        media_id = data['media_id']
        
        await state.update_data(episodes_in_season=episodes_in_season)
        await state.update_data(current_episode=1)
        await state.set_state(SeriesUpload.episode_video)
        
        await message.answer(
            f"Сезон {current_season}, серия 1 из {episodes_in_season}\n"
            f"Отправьте видео для этой серии:"
        )
        
    except ValueError:
        await message.answer("Пожалуйста, введите число:")

@dp.message(SeriesUpload.episode_video, F.video)
async def upload_episode_video(message: Message, state: FSMContext):
    data = await state.get_data()
    
    await state.update_data(episode_file_id=message.video.file_id)
    await state.set_state(SeriesUpload.episode_title)
    await message.answer("Введите название серии (или /skip чтобы пропустить):")

@dp.message(SeriesUpload.episode_title)
async def upload_episode_title(message: Message, state: FSMContext):
    if message.text.lower() == "/skip":
        await state.update_data(episode_title=None)
    else:
        await state.update_data(episode_title=message.text)
    
    await state.set_state(SeriesUpload.episode_thumbnail)
    await message.answer("Отправьте обложку серии (фото) или /skip чтобы пропустить:")

@dp.message(SeriesUpload.episode_thumbnail, F.photo)
async def upload_episode_thumbnail(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(episode_thumbnail=file_id)
    await save_episode(state, message)

@dp.message(SeriesUpload.episode_thumbnail, F.text == "/skip")
async def skip_episode_thumbnail(message: Message, state: FSMContext):
    await state.update_data(episode_thumbnail=None)
    await save_episode(state, message)

async def save_episode(state: FSMContext, message: Message):
    data = await state.get_data()
    
    db.add_episode(
        media_id=data['media_id'],
        season_number=data['current_season'],
        episode_number=data['current_episode'],
        file_id=data['episode_file_id'],
        title=data.get('episode_title'),
        thumbnail=data.get('episode_thumbnail'),
        duration=message.video.duration if message.video else None
    )
    
    episode_count = data.get('episode_count', 0) + 1
    await state.update_data(episode_count=episode_count)
    
    if data['current_episode'] < data['episodes_in_season']:
        await state.update_data(current_episode=data['current_episode'] + 1)
        await state.set_state(SeriesUpload.episode_video)
        await message.answer(
            f"Сезон {data['current_season']}, серия {data['current_episode'] + 1} из {data['episodes_in_season']}\n"
            f"Отправьте видео для этой серии:"
        )
    elif data['current_season'] < data['total_seasons']:
        await state.update_data(current_season=data['current_season'] + 1)
        await state.set_state(SeriesUpload.current_episode)
        await message.answer(f"Сезон {data['current_season'] + 1} из {data['total_seasons']}")
        await message.answer(f"Введите количество серий в {data['current_season'] + 1} сезоне:")
    else:
        db.update_media_episodes_count(data['media_id'], episode_count)
        await message.answer(
            f"✅ Сериал успешно загружен!\n"
            f"ID: {data['media_id']}\n"
            f"Название: {data['title']}\n"
            f"Всего серий: {episode_count}"
        )
        await state.clear()

@dp.message(F.text == "📊 Статистика")
async def show_statistics(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    stats = db.get_statistics()
    
    text = (
        f"📊 Статистика бота\n\n"
        f"Всего тайтлов: {stats['total']}\n"
        f"🎬 Фильмов: {stats['movies']}\n"
        f"📺 Сериалов: {stats['series']}\n"
        f"🍥 Аниме-фильмов: {stats['anime_movies']}\n"
        f"🍥 Аниме-сериалов: {stats['anime_series']}\n"
        f"📹 Всего серий: {stats['total_episodes']}"
    )
    
    await message.answer(text)

@dp.message(F.text == "🗑 Удалить контент")
async def delete_content_start(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    
    media_list = db.get_all_media()
    
    if not media_list:
        await message.answer("Нет контента для удаления.")
        return
    
    await message.answer(
        "Выберите контент для удаления:",
        reply_markup=kb.get_delete_media_keyboard(media_list)
    )

@dp.callback_query(F.data.startswith("delete_"))
async def delete_content(callback: CallbackQuery):
    media_id = int(callback.data.split("_")[1])
    media = db.get_media_by_id(media_id)
    
    if not media:
        await callback.answer("Контент не найден!", show_alert=True)
        return
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить",
                    callback_data=f"confirm_delete_{media_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data=f"cancel_delete"
                )
            ]
        ]
    )
    
    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить '{media['title']}'?\n"
        f"Это действие нельзя отменить!",
        reply_markup=confirm_keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete(callback: CallbackQuery):
    media_id = int(callback.data.split("_")[2])
    
    if db.delete_media(media_id):
        await callback.message.edit_text("✅ Контент успешно удален!")
    else:
        await callback.message.edit_text("❌ Ошибка при удалении контента!")
    
    await callback.answer()

@dp.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    await callback.message.edit_text("❌ Удаление отменено.")
    await callback.answer()

@dp.message(F.text == "⬅️ Назад")
async def back_to_main(message: Message):
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer(
            "Главное меню:",
            reply_markup=kb.get_admin_keyboard()
        )

@dp.message()
async def handle_unknown(message: Message):
    await message.answer(
        "Используйте инлайн-режим для поиска:\n"
        f"Напишите {config.BOT_USERNAME} и название фильма"
    )

async def main():
    db.init_db()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())