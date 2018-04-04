from nougat import Nougat
from nougat._router import Router, ResourceRouting, get, post, param
import motor.motor_asyncio
from snownlp import normal
from bson import ObjectId

app = Nougat()

router = Router()

con = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
db = con.douban


class CommentTagger(ResourceRouting):

    @get('/comment')
    async def get_comment(self):
        untagged_comment = await db.comments.find_one({'tag': {'$exists': False}})
        #
        await db.comments.update_one({'_id': untagged_comment['_id']}, {'$set': {'tag': True}})
        return {
            'id': str(untagged_comment['_id']),
            'content': untagged_comment['content']
        }
        # return 'hello'

    @post('/sentence')
    @param('sentence', str, location='form')
    @param('tag', str, location='form')
    async def add_sentence(self):
        """
        tag: neutral, happiness, like, sadness, disgust, anger, fear, surprise
        :return:
        """

        await db.sentences.insert({
            'sentence': self.params.sentence,
            'tag': self.params.tag
        })
        return 'ok'

    @post('/comment/:id')
    @param('id', str, location='url')
    async def tag_comment(self):
        try:

            await db.comments.update_one({'_id': ObjectId(self.params.id)}, {'$set': {'tag': True}})
        except:
            return 'error'

        else:
            return 'ok'


async def options_allow(req, res, next):
    if not req.method.upper() == 'OPTIONS':
        await next()
    res.set_header('Access-Control-Allow-Origin', '*')
    res.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, DELETE, PUT, PATCH')
    res.set_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

app.use(options_allow)

router.add(CommentTagger)

app.use(router)

app.run(debug=True)
