import requests

class RequestHandler:
    video_url = 'https://api.search.nicovideo.jp/api/v2/video/contents/search'
    video_base = "https://nico.ms"
    default_sort = "viewCounter"
    default_targets = "title,description,tags"
    # // 動画物体をGET
    @staticmethod
    def get_video(**kwargs):
        query = kwargs.get("q")
        if not 'targets' in kwargs:
            targets = RequestHandler.default_targets
        else:
            sort = kwargs.get("sort")
        if not 'sort' in kwargs:
            sort = RequestHandler.default_sort
        else:
            sort = kwargs.get("sort")
        headers = {
        'User-Agent': "Python Wax library"
        }
        payload = {
        'q': query,
        'targets': targets,
        'fields': "title,contentId,description,viewCounter,thumbnailUrl,lengthSeconds,startTime,commentCounter,channelId,tags",
        '_sort': sort,
        "_context": "NicoWax Python Library"
        }
        response = requests.get(RequestHandler.video_url, params=payload, headers=headers)
        json = response.json()
        list_of_video = []
        for video_data in json["data"]:
            vid = RequestHandler.Video(contentId=video_data["contentId"],title=video_data["title"],description=video_data["description"], viewCounter=video_data["viewCounter"], thumbnailUrl=video_data["thumbnailUrl"], lengthSeconds=video_data["lengthSeconds"], uploadDate=video_data["startTime"], commentCount=video_data["commentCounter"], channelId=video_data["channelId"], tags=video_data["tags"])
            list_of_video.append(vid)
        if len(list_of_video)>0: return list_of_video
        return None

    class Video:
        def __init__(self, contentId, title, description, viewCounter, thumbnailUrl, lengthSeconds, uploadDate, commentCount, channelId, tags):
            self.contentId = contentId
            self.contentUrl = RequestHandler.video_base+"/"+str(contentId)
            self.title = title
            self.description = description
            self.viewCounter = viewCounter
            self.thumbnailUrl = thumbnailUrl
            self.lengthSeconds = lengthSeconds
            self.uploadDate = uploadDate
            self.commentCount = commentCount
            self.channelId = channelId
            self.tags = tags
        def __str__(self):
            return self.contentUrl
