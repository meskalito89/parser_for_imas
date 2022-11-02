import vk_api
from sqlalchemy.orm import Session
from models.vk_models import Post, Reaction_vk
from pdb import set_trace
from vk_post_parser import get_groups, get_owner_id_post_id_for_sarch_method,\
    vk_session, engine, add_reaction_in_session, config
from vk_api.execute import VkFunction


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def get_post_by_owner_id_post_id(owner_id_post_id: list):
    """В вк каждый пост имеет уникальное значение 
    которое выглядит как номер группы нижнее подчеркивание номер поста
    Например 
    -1232123_3212321 """
    
    vkbot = vk_api.vk_api.VkApi(**config)
    for post_chank in chunker(owner_id_post_id, 100):
        chank = vkbot.method('wall.getById', values={'posts':",".join(post_chank)})
        yield chank

def save_reactions(posts):
    with Session(engine) as session:
        for post in posts:
            add_reaction_in_session(post, session)
        session.commit()
        

if __name__ == "__main__":

    owner_id_post_id = get_owner_id_post_id_for_sarch_method()
    chanks = get_post_by_owner_id_post_id(owner_id_post_id)
    for chank in chanks:
        save_reactions(chank)
