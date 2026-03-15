# keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict

# ==================== REPLY KEYBOARDS ====================

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для администратора"""
    keyboard = [
        [
            KeyboardButton(text="📤 Загрузить фильм"),
            KeyboardButton(text="📤 Загрузить сериал")
        ],
        [
            KeyboardButton(text="🍥 Загрузить аниме фильм"),
            KeyboardButton(text="🍥 Загрузить аниме сериал")
        ],
        [
            KeyboardButton(text="📊 Статистика"),
            KeyboardButton(text="🗑 Удалить контент")
        ],
        [
            KeyboardButton(text="⬅️ Назад")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_user_keyboard() -> ReplyKeyboardMarkup:
    """Пустая клавиатура для обычных пользователей"""
    return ReplyKeyboardMarkup(keyboard=[[]], resize_keyboard=True)

# ==================== INLINE KEYBOARDS ====================

def get_start_inline_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-кнопки для начала поиска и информации о Sigma"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔍 Начать поиск", 
                    switch_inline_query_current_chat=""
                )
            ],
            [
                InlineKeyboardButton(
                    text="❓ Кто такой Sigma?", 
                    callback_data="sigma_info"
                )
            ]
        ]
    )
    return keyboard

def get_sigma_info_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для возврата из информации о Sigma"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", 
                    callback_data="back_to_start"
                )
            ]
        ]
    )
    return keyboard

def get_media_action_keyboard(media_id: int) -> InlineKeyboardMarkup:
    """Кнопки действий для медиа (смотреть/инфо)"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="▶️ Смотреть", 
                    callback_data=f"watch_{media_id}"
                ),
                InlineKeyboardButton(
                    text="ℹ️ Инфо", 
                    callback_data=f"info_{media_id}"
                )
            ]
        ]
    )
    return keyboard

def get_seasons_keyboard(media_id: int, total_seasons: int) -> InlineKeyboardMarkup:
    """Клавиатура со списком сезонов"""
    buttons = []
    row = []
    
    for season in range(1, total_seasons + 1):
        row.append(InlineKeyboardButton(
            text=f"🎬 Сезон {season}",
            callback_data=f"season_{media_id}_{season}"
        ))
        
        if len(row) == 2:  # По 2 кнопки в ряд
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    # Кнопка назад к информации
    buttons.append([InlineKeyboardButton(
        text="⬅️ Назад", 
        callback_data=f"info_{media_id}"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_episodes_keyboard(media_id: int, season: int, episodes: List[Dict]) -> InlineKeyboardMarkup:
    """Клавиатура со списком серий"""
    buttons = []
    row = []
    
    for episode in episodes:
        ep_num = episode['episode_number']
        row.append(InlineKeyboardButton(
            text=f"📺 {ep_num}",
            callback_data=f"episode_{media_id}_{season}_{ep_num}"
        ))
        
        if len(row) == 5:  # По 5 кнопок в ряд
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    # Кнопка назад к сезонам
    buttons.append([InlineKeyboardButton(
        text="⬅️ Назад к сезонам", 
        callback_data=f"seasons_{media_id}"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_delete_media_keyboard(media_list: List[Dict]) -> InlineKeyboardMarkup:
    """Клавиатура для удаления контента"""
    buttons = []
    
    for media in media_list:
        # Эмодзи в зависимости от типа
        emoji = {
            'movie': '🎬',
            'series': '📺',
            'anime_movie': '🍥',
            'anime_series': '🍥'
        }.get(media['type'], '📹')
        
        title = media['title']
        if len(title) > 30:
            title = title[:27] + "..."
        
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {title} (ID: {media['id']})",
            callback_data=f"delete_{media['id']}"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_to_info_keyboard(media_id: int) -> InlineKeyboardMarkup:
    """Кнопка возврата к информации"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="⬅️ Назад к информации", 
                callback_data=f"info_{media_id}"
            )]
        ]
    )
    return keyboard