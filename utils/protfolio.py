from os import path

from aiogram.types import FSInputFile, Message
from aiogram.types.input_media_photo import InputMediaPhoto
from sqlalchemy import desc

from database.model import Project
from tasks import kb
from tasks.config import get_config
from tasks.loader import bot, sender, session, settings


async def send_project(
    user_id,
    project_number=0,
    photo_number=0,
    prevoius_message: Message = None,
):
    project_count = session.query(Project).count()
    if project_number == -1:
        project_number = project_count - 1
    elif project_number == project_count:
        project_number = 0

    project = (
        session.query(Project)
        .order_by(desc(Project.order))
        .offset(project_number)
        .limit(1)
        .first()
    )

    if project.photos:
        if photo_number >= len(project.photos):
            photo_number = 0
        elif photo_number == -1:
            photo_number = len(project.photos) - 1
        photo = project.photos[photo_number]
    else:
        photo = None

    args = get_project_args(project)

    if prevoius_message:
        if bool(prevoius_message.photo) == bool(photo):
            if photo:
                await prevoius_message.edit_media(
                    InputMediaPhoto(
                        media=photo.photo_id,
                        caption=sender.text("project", *args),
                    ),
                    reply_markup=kb.project(
                        project_number,
                        photo_number,
                        len(project.photos),
                    ),
                )
            else:
                sender.edit_message(
                    prevoius_message,
                    "project",
                    kb.project(project_number),
                    *args,
                )
            return
        else:
            await prevoius_message.delete()

    if photo:
        await sender.send_cached_media(
            user_id,
            "photo",
            photo.photo_id,
            "project",
            kb.project(
                project_number,
                photo_number,
                len(project.photos),
            ),
            *args,
        )
    else:
        await sender.message(
            user_id,
            "project",
            kb.project(project_number),
            *args,
        )


def get_project_args(project: Project):
    return [
        project.name,
        project.description,
        "\n\nСсылка на проект: " + project.link if project.link else "",
        "\n".join([tool.tool.name for tool in project.tools]),
    ]
