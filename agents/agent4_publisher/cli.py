"""Единая точка входа Агента 4 — Publisher.

Подкоманды:
    generate {post,image,carousel,stories,voice,video,stickers}    локальная генерация артефакта
    publish  {telegram,instagram,max,vk,dzen}                публикация готового файла в канал

Перенесён полезный контур из `sales_ai` без курса/Jarvis: текст, изображение,
карусель, сторис, голос, видео-задание, стикер, Telegram и Redis-события.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

GENERATE_KINDS = ("post", "image", "carousel", "stories", "voice", "video", "stickers")
PUBLISH_CHANNELS = ("telegram", "instagram", "max", "vk", "dzen")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="agent4-publisher", description="Контент-движок ВПП-студии")
    sub = p.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate", help="Локальная генерация контента")
    g.add_argument("kind", choices=GENERATE_KINDS, help="Тип артефакта")
    g.add_argument("--topic", required=True, help="Тема или бриф для LLM")
    g.add_argument("--output", help="Путь к файлу (по умолчанию — авто в output/<kind>/)")
    g.add_argument("--dry-run", action="store_true", help="Создать тестовый черновик без API")

    pub = sub.add_parser("publish", help="Публикация готового файла")
    pub.add_argument("channel", choices=PUBLISH_CHANNELS, help="Канал назначения")
    pub.add_argument("--file", required=True, help="Путь к подготовленному артефакту")
    pub.add_argument("--lead-id", help="id лида из Bitrix, если контент — ответ на конкретный запрос")
    pub.add_argument("--dry-run", action="store_true", help="Проверить маршрут без реальной публикации")

    return p


def _dispatch_generate(args: argparse.Namespace) -> int:
    if args.kind == "post":
        from agents.agent4_publisher.core.llm import generate_post_text, save_post

        text = generate_post_text(args.topic, dry_run=args.dry_run)
        path = save_post(args.topic, text, args.output)
    elif args.kind == "image":
        from agents.agent4_publisher.core.image import generate_image

        path = generate_image(args.topic, args.output, dry_run=args.dry_run)
    elif args.kind == "carousel":
        from agents.agent4_publisher.core.carousel import generate_carousel

        path = generate_carousel(args.topic, args.output, dry_run=args.dry_run)
    elif args.kind == "stories":
        from agents.agent4_publisher.core.stories import generate_stories

        path = generate_stories(args.topic, args.output, dry_run=args.dry_run)
    elif args.kind == "voice":
        from agents.agent4_publisher.core.voice import synthesize_voice

        path = synthesize_voice(args.topic, args.output, dry_run=args.dry_run)
    elif args.kind == "video":
        from agents.agent4_publisher.core.video import generate_video

        path = generate_video(args.topic, args.output, dry_run=args.dry_run)
    elif args.kind == "stickers":
        from agents.agent4_publisher.core.stickers import generate_sticker

        path = generate_sticker(args.topic, args.output, dry_run=args.dry_run)
    else:
        raise NotImplementedError(f"Неизвестный тип генерации: {args.kind}")

    print(f"OK: {args.kind} сохранён: {path}")
    return 0


def _dispatch_publish(args: argparse.Namespace) -> int:
    if args.channel == "telegram":
        from agents.agent4_publisher.posters.telegram import publish_markdown_file

        result = publish_markdown_file(args.file, lead_id=args.lead_id, dry_run=args.dry_run)
        if args.dry_run:
            print(f"OK: маршрут Telegram проверен: {result}")
            return 0
        post_id = result["event"].get("post_id") or "unknown"
        print(f"OK: опубликовано в Telegram, post_id={post_id}")
        return 0

    module_name = {
        "instagram": "instagram",
        "max": "max",
        "vk": "vk",
        "dzen": "dzen",
    }[args.channel]
    module = __import__(f"agents.agent4_publisher.posters.{module_name}", fromlist=["publish_file"])
    result = module.publish_file(args.file, lead_id=args.lead_id, dry_run=args.dry_run)
    print(f"OK: маршрут {args.channel} проверен: {result}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "generate":
        return _dispatch_generate(args)
    if args.command == "publish":
        return _dispatch_publish(args)
    parser.error(f"Неизвестная команда: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
