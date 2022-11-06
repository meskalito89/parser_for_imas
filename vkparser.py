from create_models import VkGroups, VkPosts, VkReactions
from sql_configurator import parser, get_engine
from sqlalchemy.orm import Session
import vk_api
from vk_api.exceptions import VkToolsException
from pdb import set_trace
from random import shuffle


parser.add_argument(
    '-v',
    "--vk_config_file",
    help="""Путь к файлу с токеном, логином и паролем от Вконтакте в формате json
    пример.\n
        {
            "token": "token",
            "login": "login",
            "password": "password"
        }
    """,
    required=True
)

args = parser.parse_args()
set_trace()
sql_config = read_config(args.sql_config_file)
engine = get_engine(sql_config)
sql_session = Session(engine)
tools = vk_api.VkTools(vk_client)

class VkParser:
    def __init__(self, url: str, *args, **kwargs):
        self.url = url
        self.sql_request = kwargs.get('sql_request', None)
        self.id = self.get_self_id_by_database_request() or self.get_self_id_by_http_request()
        self.chank_size = kwargs.get("chank_size", 1)
        self.limit = kwargs.get("limit", 20)
        self.post_iter = tools.get_all_iter('wall.get', self.chank_size, {'owner_id': self.id})
        
    def get_posts_from_database_filtered_by_url(self):
        with sql_session:
            all_posts_from_database_with_self_url = sql_session.query(VkPosts).filter_by(owner_id=self.id).all()
            return all_posts_from_database_with_self_url

    def get_all_posts_from_database(self):
        with sql_session:
            return sql_session.query(VkPosts).filter_by(owner_id=self.id).all()

    def get_self_id_by_database_request(self):
        with sql_session:
            id = sql_session.query(VkGroups).filter_by(link=self.url).one().id
            return id

    def get_self_id_by_http_request(self):
        group_name = self.url.split("/")[-1]
        response = vk_client.method("utils.resolveScreenName", {'screen_name': group_name})
        id = response.get("object_id", )*-1
        return id

    def parse_post(self, post):

        new_post = VkPosts(
            id = post.get('id'),
            owner_id = post.get('owner_id'),
            date = post.get('date'),
            from_id = post.get('from_id'),
            text = post.get('text'),
        )
        return new_post
    
    def parse_reactions(self, post):

        new_reaction = VkReactions(
            post_id = post.get('id'),
            owner_id = post.get('owner_id'),
            likes = post.get('likes', dict()).get('count', 0),
            reposts = post.get('reposts', dict()).get('count', 0),
            views = post.get('views', dict()).get('count', 0),
            comments = post.get('comments', dict()).get('count', 0),
        )
        return new_reaction

    def is_post_in_database(self, post):

        with sql_session:
            posts = self.get_posts_from_database_filtered_by_url()
            exist = sql_session.query(
                VkPosts.id, VkPosts.owner_id).filter_by(owner_id=post.get('owner_id'), id=post.get("id")
                ).all()
            if exist:
                return True
            return False

    def get_min_post_id_from_database(self):
        posts = self.get_posts_from_database_filtered_by_url()
        min_id = min([post.id for post in posts] or [1]) 
        return min_id

    def save_to_database(self, sqlalchemy_obj):

        with sql_session:
            try:
                sql_session.add(sqlalchemy_obj)
                sql_session.commit()
                print('saved ', self.url, sqlalchemy_obj)
            except Exception as err:
                pass

    def parse_first_limit_posts(self):
        for _ in range(self.limit):
            try:
                post = next(self.post_iter)
                if self.is_post_in_database(post):
                    continue
                new_reaction = self.parse_reactions(post)
                new_post = self.parse_post(post)
                self.save_to_database(new_post)
                self.save_to_database(new_reaction)

            except StopIteration as stop_error:
                print('stop iteration')
                break
            except VkToolsException as vk_exception:
                print(f'group {self.url} blocked')
                break

    def this_is_new_channel(self):
        return not self.get_posts_from_database_filtered_by_url()


    def start(self):
        # set_trace()
        count = 0
        if self.this_is_new_channel():
            self.parse_first_limit_posts()
            return 

        while True:
            try:
                post = next(self.post_iter)
            except StopIteration as stop_error:
                print('stop iteration')
                break
            except VkToolsException as vk_exception:
                print(f'group {self.url} blocked')
                break

            new_reaction = self.parse_reactions(post)
            new_post = self.parse_post(post)

            if self.is_post_in_database(post):
                self.save_to_database(new_reaction)
                count += 1
                continue

            else:
                if count > 0:
                    break
                else:
                    self.save_to_database(new_reaction)
                    self.save_to_database(new_post)

if __name__ == "__main__":
    with sql_session:
        urls = [group.link for group in sql_session.query(VkGroups).all()]
        shuffle(urls)
        for url in urls:
            parser = VkParser(url)
            parser.start()