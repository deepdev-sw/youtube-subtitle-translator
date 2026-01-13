import re
import json
import requests
from bs4 import BeautifulSoup
import pytube

class ChannelProcessor:
    def __init__(self):
        self.url_patterns = {
            'channel': [
                r'(?:https?://)?(?:www\.)?youtube\.com/@([a-zA-Z0-9_-]+)'
            ],
            'playlist': [
                r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)'
            ],
            'video': [
                r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)'
            ]
        }
    
    def get_url_type_and_id(self, url):
        """
        从YouTube URL中提取类型和ID
        返回 (url_type, id) 元组，其中 url_type 是 'channel', 'playlist', 或 'video'
        """
        for url_type, patterns in self.url_patterns.items():
            for pattern in patterns:
                match = re.match(pattern, url)
                if match:
                    return url_type, match.group(1)
        
        raise ValueError("无法从URL中提取类型和ID")
    
    def get_channel_id(self, url):
        """
        从YouTube频道URL中提取频道ID或用户名
        """
        for pattern in self.url_patterns['channel']:
            match = re.match(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError("无法从URL中提取频道ID或用户名")
    
    def get_channel_playlists(self, channel_id):
        """
        获取频道下的所有播放列表
        """
        playlists = []
        
        # 设置请求头，模拟真实浏览器，移除 Accept-Encoding 让 requests 自动处理压缩
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
            # 直接从网络获取播放列表页面，添加超时设置
        response = requests.get(f"https://www.youtube.com/@{channel_id}/playlists", headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise ValueError(f"无法访问频道的播放列表页面，状态码: {response.status_code}")
        
        # 确保内容被正确解码（处理压缩响应）
        response.encoding = response.apparent_encoding
        html_text = response.text
        
        # 提取ytInitialData对象
        yt_initial_data_match = re.search(r'var ytInitialData = ({.*?});', html_text, re.DOTALL)
        
        if yt_initial_data_match:
            yt_initial_data_str = yt_initial_data_match.group(1)
            try:
                yt_initial_data = json.loads(yt_initial_data_str)
                
                # 解析播放列表数据
                # 查找播放列表所在的section
                contents = yt_initial_data.get('contents', {})
                two_column_browse_results_renderer = contents.get('twoColumnBrowseResultsRenderer', {})
                tabs = two_column_browse_results_renderer.get('tabs', [])
                
                for tab in tabs:
                    has_playlists = False  # 初始化变量
                    tab_renderer = tab.get('tabRenderer', {})
                    content = tab_renderer.get('content', {})
                    section_list_renderer = content.get('sectionListRenderer', {})
                    contents = section_list_renderer.get('contents', [])
                    
                    # 遍历内容，查找包含gridRenderer的部分
                    for content_item in contents:
                        item_section_renderer = content_item.get('itemSectionRenderer', {})
                        item_contents = item_section_renderer.get('contents', [])
                        
                        for item in item_contents:
                            grid_renderer = item.get('gridRenderer', {})
                            items = grid_renderer.get('items', [])
                            
                            # 检查items中是否包含lockupViewModel（新结构）
                            if any('lockupViewModel' in grid_item for grid_item in items):
                                has_playlists = True
                                # 这是播放列表标签
                                for grid_item in items:
                                    lockup_view_model = grid_item.get('lockupViewModel', {})
                                    if lockup_view_model:
                                        # 提取播放列表信息
                                        # 从contentId获取playlistId
                                        playlist_id = lockup_view_model.get('contentId', '')
                                        
                                        # 从metadata中获取标题
                                        metadata = lockup_view_model.get('metadata', {})
                                        lockup_metadata = metadata.get('lockupMetadataViewModel', {})
                                        title_obj = lockup_metadata.get('title', {})
                                        title = title_obj.get('content', '')
                                        
                                        if playlist_id and title:
                                            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                                            playlists.append({
                                                "id": playlist_id,
                                                "url": playlist_url,
                                                "title": title
                                            })
                                break  # 找到播放列表后退出循环
                        if has_playlists:
                            break  # 找到播放列表后退出循环
                    if has_playlists:
                        break  # 找到播放列表后退出循环
            except json.JSONDecodeError:
                print("无法解析ytInitialData")
        # 去重，确保每个播放列表只添加一次
        unique_playlists = []
        seen_ids = set()
        for playlist in playlists:
            if playlist["id"] not in seen_ids:
                seen_ids.add(playlist["id"])
                unique_playlists.append(playlist)
        
        return unique_playlists
    
    def get_playlist_videos(self, playlist_id):
        """
        获取播放列表中的所有视频
        """
        videos = []
        
        # 直接解析播放列表网页获取视频，不使用pytube.Playlist
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        print(f"播放列表 URL: {playlist_url}")
        
        # 设置请求头，模拟真实浏览器
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # 获取播放列表页面
        response = requests.get(playlist_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"无法访问播放列表页面，状态码: {response.status_code}")
            return videos
        
        # 提取ytInitialData
        yt_initial_data_match = re.search(r'var ytInitialData = ({.*?});', response.text, re.DOTALL)
        if not yt_initial_data_match:
            print("未找到ytInitialData")
            return videos
        
        yt_initial_data = json.loads(yt_initial_data_match.group(1))
        
        # 查找视频列表
        def find_video_ids(data):
            video_ids = []
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "videoId":
                        video_ids.append(value)
                    video_ids.extend(find_video_ids(value))
            elif isinstance(data, list):
                for item in data:
                    video_ids.extend(find_video_ids(item))
            return video_ids
        
        video_ids = find_video_ids(yt_initial_data)
        # 去重
        video_ids = list(set(video_ids))
        
        print(f"解析到 {len(video_ids)} 个视频 ID")
        
        # 构建视频信息
        for video_id in video_ids:
            video_info = self.get_single_video(video_id)
            if video_info:
                videos.append(video_info)
        
        return videos
    
    def get_single_video(self, video_id):
        """
        获取单个视频的详细信息
        """
        
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # 使用 requests 获取视频页面，避免依赖 pytube
        # requests 和 BeautifulSoup 已在文件开头导入
        
        # 设置请求头，模拟浏览器访问
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # 获取视频页面
        response = requests.get(video_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 获取视频标题
        title = soup.find("title").text if soup.find("title") else f"视频 {video_id}"
        # 移除标题中的 " - YouTube"
        title = title.replace(" - YouTube", "")
        
        # 获取视频描述（尝试从 meta 标签或页面内容中获取）
        description = ""
        meta_description = soup.find("meta", property="og:description")
        if meta_description:
            description = meta_description.get("content", "")
        
        # 获取发布日期（尝试从 meta 标签中获取）
        publish_date = None
        meta_publish_date = soup.find("meta", itemprop="datePublished")
        if meta_publish_date:
            publish_date = meta_publish_date.get("content", None)
        
        # 添加视频信息到列表
        video_info = {
            "title": title,
            "url": video_url,
            "video_id": video_id,
            "publish_date": publish_date,
            "description": description,
        }
        
        return video_info
    
    def get_channel_videos(self, id, id_type='channel'):
        """
        获取频道、播放列表或单个视频中的所有视频
        
        参数:
            id: 频道ID、播放列表ID或视频ID
            id_type: 'channel', 'playlist', 或 'video'
        """
        videos = []
        
        if id_type == 'channel':
            # 处理频道：先获取所有播放列表
            playlists = self.get_channel_playlists(id)
            
            if not playlists:
                print(f"频道 {id} 下没有找到播放列表")
                return videos
            
            # 遍历每个播放列表获取视频
            for playlist in playlists:
                print(f"正在获取播放列表 {playlist['title']} ({playlist['id']}) 中的视频")
                playlist_videos = self.get_playlist_videos(playlist['id'])
                videos.extend(playlist_videos)
        elif id_type == 'playlist':
            # 处理播放列表
            videos = self.get_playlist_videos(id)
        elif id_type == 'video':
            # 处理单个视频
            videos.append(self.get_single_video(id))
        
        return videos
    
    def get_video_info(self, video_url):
        """
        获取单个视频的信息
        """
        yt = pytube.YouTube(video_url)
        return {
            "title": yt.title,
            "url": video_url,
            "video_id": yt.video_id,
            "publish_date": yt.publish_date,
            "description": yt.description
        }
