from create_models import VkGroups, VkPosts, VkReactions
from configurator import sql_session, parser, read_config
import vk_api
from pdb import set_trace

# parser.add_argument("--vk_config_file",
#     help="""Путь к файлу с токеном, логином и паролем от Вконтакте в формате json
#     пример.\n
#         {
#             "token": "token",
#             "login": "login",
#             "password": "password"
#         }
#     """,
#     required=True
# )
# args = parser.parse_args()

vk_config = read_config('/etc/imas_parser.conf/vk_bot_conf.json')
vk_client = vk_api.VkApi(**vk_config)

class VkParser:
    def __init__(self, url: str, *args, **kwargs):
        self.url = url
        self.sql_request = kwargs.get('sql_request', None)
        self.id = self.get_id_from_db() or self.get_id_from_vk()
        
    def get_posts_from_database_with_self_url(self):
        with sql_session:
            all_posts_from_database_with_self_url = sql_session.query(VkPosts).filter_by(owner_id=self.id).all()
            return all_posts_from_database_with_self_url

    def get_all_posts_from_database(self):
        with sql_session:
            return sql_session.query(VkPosts).filter_by(owner_id=self.id).all()

    def get_id_from_db(self):
        with sql_session:
            id = sql_session.query(VkGroups).filter_by(link=self.url).one().id
            return id

    def get_id_from_vk(self):
        group_name = self.url.split("/")[-1]
        response = vk_client.method("utils.resolveScreenName", {'screen_name': group_name})
        id = response.get("object_id", )*-1
        return id

parser = VkParser("https://vk.com/vk.fact")
set_trace()