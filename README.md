# 🦊 Fox2-clone

Open-source аналог программы **Fox2** для автоматизации создания видео из текстового сценария.

Полный пайплайн: **сценарий → разбивка на сцены → промты → озвучка → картинки → видео → нарезка сеток → финальная сборка** с переходами и анимациями.

> Это не реверс-инжиниринг оригинала. Это самостоятельная реализация по мотивам интерфейса/идей,
> с упором на **бесплатные** и **open-source** альтернативы (Edge TTS, Pollinations, локальный
> ffmpeg, Ollama/LM Studio), плюс опциональные API/браузерные интеграции для платных
> сервисов.

---

## Возможности

- 🦊 **GUI на CustomTkinter** с тёмной темой и теми же 7 вкладками, что в оригинале:
  *Настройки · Озвучка · Медиа · Видео · Браузер · Сборка · Озвучка Веб*
- 📝 **Уникализатор сценария** (через LLM или локальный словарный шафл) и автоматическое
  разбиение по предложениям/группам.
- 🤖 **LLM-провайдеры**: Ollama, LM Studio, OpenAI, Anthropic (Claude), Google Gemini, xAI Grok.
- 🔊 **TTS-провайдеры**: Edge TTS (бесплатно), ElevenLabs, локальный Piper, AI Studio (через браузер).
- 🎨 **Картинки**: Pollinations.ai (бесплатно), Stable Diffusion WebUI (локально), и заглушки
  для Nano Banana / Grok Imagine / Google Flow через браузер.
- 🎬 **Видео**: локальная анимация ffmpeg (Ken Burns, Zoom In/Out, Pan, Fade) + заглушки
  для Veo3 / Grok через браузер.
- ✂️ **Нарезка сеток 2×2** (PIL для картинок, ffmpeg для видео).
- 🧩 **Финальная сборка** ffmpeg: переходы (fade, fade-to-black/white), анимации картинок,
  микширование аудио.
- 🌐 **Менеджер аккаунтов / координат** для браузерной автоматизации
  (Playwright-профили + pyautogui-захват координат, как в оригинале).

---

## Установка

Требуется Python 3.10+ и установленный `ffmpeg` в PATH.

### Быстрый старт — двойной клик

После того как ты клонировал репозиторий, **просто кликни два раза** по нужному файлу
в корне папки:

| Платформа | Файл |
|---|---|
| Windows | `run.bat` |
| macOS | `run.command` |
| Linux | `run.sh` (сначала: `chmod +x run.sh`) |

**Первый запуск** создаст виртуальное окружение `.venv/` рядом с проектом и поставит
зависимости (1–3 минуты). **Все последующие** — стартуют GUI за ~1 секунду.

Скрипт сам проверит, что Python и ffmpeg доступны, и подскажет, как их поставить
если нет.

### Установка вручную (без лаунчера)

```bash
git clone https://github.com/sagarjagtap20000-lang/fox2-clone.git
cd fox2-clone
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e .
```

Опциональные группы зависимостей:

```bash
pip install -e ".[browser]"        # Playwright (браузерная автоматизация)
pip install -e ".[openai]"         # OpenAI SDK (не обязательно — есть REST-обёртка)
pip install -e ".[anthropic]"      # Anthropic SDK
pip install -e ".[gemini]"         # google-generativeai
pip install -e ".[elevenlabs]"     # ElevenLabs SDK
pip install -e ".[local-llm]"      # ollama Python client
pip install -e ".[all]"            # всё сразу
pip install -e ".[dev]"            # ruff + pytest + mypy
```

Для координатной автоматизации (как в оригинальном Fox2) — `pip install pyautogui`.

Для браузерных flows установи браузеры Playwright:

```bash
python -m playwright install chromium
```

Для Google/Veo лучше использовать системный Chrome, а не bundled Chromium: Google часто
блокирует вход во «встроенные»/автоматизированные браузеры. Установи Chrome/Chromium в
систему и открой его через вкладку **«Браузер»** — Fox создаёт отдельные постоянные
профили в `~/Fox2Clone/chrome_profiles`, поэтому cookies и Google login сохраняются.

---

## Запуск

```bash
fox2                # стандартный запуск GUI
fox2 --debug        # с DEBUG логами
```

Окно: слева — поле сценария, базовые настройки (стиль/разрешение/группировка) и кнопка
**▶ Запустить**, которая прогоняет промты → картинки → озвучку. Справа — 7 вкладок с
тонкими настройками.

Финальная склейка делается во вкладке **«Сборка»**: настрой переходы, анимации, при
желании используй разрезанные папки (`images_split` / `video_split`), нажми «🎬 Собрать
финальное видео» — получишь `final/output.mp4`.

---

## Структура проекта на диске

Каждый прогон создаёт папку в `~/Fox2Clone/projects/Project_<timestamp>`:

```
Project_1731366000/
├── project_meta.json     # сценарий, сцены, группы, выбранные настройки
├── groups_meta.json      # удобный для глаза JSON со списком групп
├── audio/                # озвучка (mp3)
├── images/               # исходные картинки (если single) или сетки 2×2
├── images_split/         # картинки после разрезки сеток
├── video/                # анимация / image-to-video
├── video_split/          # видео после разрезки сеток
└── final/                # output.mp4 — финальная сборка
```

---

## Куда стартовать без ключей

Полностью бесплатная конфигурация по умолчанию:

| Назначение | Провайдер | Ключ нужен? |
|------------|-----------|-------------|
| LLM (промты, уникализатор) | Ollama (`llama3.1`) | нет, ставится локально |
| TTS | Edge TTS | нет |
| Картинки | Pollinations.ai | нет |
| Видео | Локальный ffmpeg (Ken Burns) | нет |
| Финальная сборка | Локальный ffmpeg | нет |

LLM-промты — опциональны: если Ollama не запущена, используются локальные
шаблонные промты (`fox2.core.prompts.build_local_prompt`), и пайплайн всё равно отработает.

---

## Архитектура

```
src/fox2/
├── app.py                 # точка входа (fox2 в PATH)
├── core/                  # модели проекта, разбивка сценария, ассемблер, грид-сплит
│   ├── assembly.py
│   ├── grid.py
│   ├── models.py
│   ├── pipeline.py
│   ├── project.py
│   ├── prompts.py
│   ├── script.py
│   ├── settings.py
│   └── uniquifier.py
├── providers/
│   ├── llm/               # ollama, openai, anthropic, gemini, grok, lmstudio
│   ├── tts/               # edge, elevenlabs, piper
│   ├── image/             # pollinations, sd_webui (+ заглушки для браузерных)
│   ├── video/             # local_kenburns (+ заглушки)
│   └── browser/           # профили Playwright, кликер по координатам
├── ui/                    # CustomTkinter UI
│   ├── main_window.py     # главное окно (как у Fox2)
│   ├── tabs/              # 7 вкладок: settings/voicing/media/video/browser/assembly/voice_web
│   ├── state.py           # AppState + фоновая очередь задач
│   ├── theme.py           # цвета (тёмная фиолетовая)
│   └── widgets.py         # переиспользуемые виджеты
└── utils/
    ├── ffmpeg.py
    ├── logging.py
    └── paths.py
```

Все провайдеры — независимые модули с общей сигнатурой (`fox2.providers.base`):
`LLMProvider.complete`, `TTSProvider.synthesize`, `ImageProvider.generate`,
`VideoProvider.animate`. Фабрики (`providers/*/factory.py`) собирают нужного провайдера
по имени из `AppSettings`.

---

## Разработка

```bash
pip install -e ".[dev]"
ruff check src tests
pytest -q
```

---

## Veo/Flow: несколько аккаунтов и кредиты

Вкладка **«Браузер»** теперь работает как менеджер Chrome-профилей:

1. Создай профиль для каждого Google-аккаунта (`acc_1`, `acc_2`, ...).
2. Нажми **«Открыть Chrome»** и войди в нужный Google-аккаунт один раз. Для каждого
   профиля используется отдельная папка `user-data-dir`, поэтому аккаунты не смешиваются.
3. Укажи дневной лимит кредитов, по умолчанию 50.
4. Когда провайдер `flow_browser` использует профиль, счётчик уменьшается. Когда кредиты
   закончились или профиль поставлен на паузу, выбирается следующий доступный профиль.
5. Кнопка **«Сброс дня»** обнуляет счётчики на следующий день.

Если нужно использовать расширение автоматизации из Chrome Web Store, установи его в
каждый профиль вручную или распакуй extension в локальную папку и укажи путь в поле
**«Папка расширения»**. Fox загрузит unpacked extension через `--load-extension`. `.crx`
из Chrome Web Store напрямую не встраивается в репозиторий, потому что это сторонний
закрытый пакет.

CI крутит lint+тесты на Python 3.10/3.11/3.12 в GitHub Actions.

---

## Лицензия

MIT — см. `LICENSE`.
