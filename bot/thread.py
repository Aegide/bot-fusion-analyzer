from discord import Member, Message, NotFound, TextChannel, Thread
import utils


PREFIX = "//"
ROLE_ID_SPRITE_MANAGER = 900867033175040101
BRUTEFORCE_THREAD_ARCHIVE = "**== THREAD ARCHIVED ==**"
NORMAL_THREAD_ARCHIVE = "== THREAD ARCHIVED =="


async def handle_spritework(message:Message):
    if is_thread_command(message):
        await handle_thread(message)


def is_thread_command(message:Message):
    return PREFIX == message.content[0:2] and message.content[2:] == "kill"


async def handle_thread(message:Message):
    thread = get_thread(message)
    if can_manage_thread(message, thread):
        utils.log_event(f"[[{thread.name}]]", message)
        await archive_thread(message, thread)
    else:
        await thread.send(f"<@!{message.author.id}> you are not allowed to archive this thread.")


def get_thread(message:Message) -> Thread:
    if isinstance(message.channel, Thread):
        return message.channel
    else:
        raise TypeError(message.channel)


def can_manage_thread(message:Message, thread:Thread):
    return is_thread_owner(message, thread) or is_sprite_manager(message)


def is_sprite_manager(message:Message):
    result = False
    if isinstance(message.author, Member):
        roles_author = message.author.roles
        for role in roles_author:
            if role.id == ROLE_ID_SPRITE_MANAGER:
                result = True
    return result


def is_thread_owner(message:Message, thread:Thread):
    return message.author.id == thread.owner_id


async def archive_thread(message:Message, thread:Thread):
    if not is_thread_owner(message, thread):
        await thread.send(BRUTEFORCE_THREAD_ARCHIVE)
    else:
        await thread.send(NORMAL_THREAD_ARCHIVE)

    await delete_original_message(thread)
    await close_thread(thread)


async def delete_original_message(thread: Thread):
    original_message_id = thread.id
    spritework = thread.guild.get_channel(thread.parent_id)
    if isinstance(spritework, TextChannel) :
        original_message = spritework.get_partial_message(original_message_id)
        try:
            await original_message.delete()
        except NotFound as nf:
            pass


async def close_thread(thread: Thread):
    await thread.edit(archived=True)  # makes the thread "old"
    # await thread.edit(locked=True)  # makes the thread "locked" + "old"

