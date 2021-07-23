from datetime import datetime

from .request_api import RequestAPI


class SonarrAPI(RequestAPI):
    """API wrapper for Sonarr endpoints."""

    def construct_series_json(
        self,
        tvdb_id,
        quality_profile_id,
        root_dir,
        season_folder=True,
        monitored=True,
        ignore_episodes_with_files=False,
        ignore_episodes_without_files=False,
        search_for_missing_episodes=False,
    ):
        """Searches for new shows on trakt and returns Series json to add

        Args:
            [Required] tvdb_id (int)
            [Required] quality_profile_id (int)
            [Required] root_dir (str)
            [Optional] season_folder (bool)
            [Optional] monitored (bool)
            [Optional] ignore_episodes_with_files (bool)
            [Optional] ignore_episodes_without_files (bool)
            [Optional] search_for_missing_episodes (bool)
        Returns:
            JSON Response (dict)
        """
        res = self.lookup_series(tvdb_id)
        s_dict = res[0]
        if not monitored and s_dict.get("seasons"):
            for season in s_dict["seasons"]:
                season["monitored"] = False

        series_json = {
            "title": s_dict["title"],
            "seasons": s_dict["seasons"],
            "path": root_dir + s_dict["title"],
            "qualityProfileId": quality_profile_id,
            "seasonFolder": season_folder,
            "monitored": monitored,
            "tvdbId": tvdb_id,
            "images": s_dict["images"],
            "titleSlug": s_dict["titleSlug"],
            "addOptions": {
                "ignoreEpisodesWithFiles": ignore_episodes_with_files,
                "ignoreEpisodesWithoutFiles": ignore_episodes_without_files,
                "searchForMissingEpisodes": search_for_missing_episodes,
            },
        }
        return series_json

    ## CALENDAR

    # GET /calendar
    def get_calendar(self, start_date=None, end_date=None):
        """Retrieves info about when series were/will be downloaded.
        If no start and end, retrieves series airing today and tomorrow.

        Args:
            [Optional] start_date (datetime) - ISO 8601
            [Optional] end_date (datetime) - ISO 8601
        Returns:
            JSON Response (dict)
        """
        path = "/api/calendar"
        params = {}
        if start_date:
            params["start"] = datetime.strptime(start_date, "%Y-%m-%d").strftime(
                "%Y-%m-%d"
            )
        if end_date:
            params["end"] = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")

        res = self.request_get(path, params=params)
        return res

    ## COMMAND

    # GET /command
    def get_command(self, id_=None):
        """Queries the status of a previously
        started command, or all currently started commands.

        Args:
            [Optional] id (int) Unique ID of command
        Returns:
            JSON Response (dict)
        """
        if id_:
            path = f"/api/command/{id_}"
        else:
            path = "/api/command"

        res = self.request_get(path)
        return res

    # POST /command
    def set_command(self, name, **kwargs):
        """Performs any of the predetermined Sonarr command routines.

        Args:
            [Required] name (str).
        Kwargs:
            For command names and additional kwargs:
            See https://github.com/Sonarr/Sonarr/wiki/Command
        Returns:
            JSON Response (dict)
        """
        path = "/api/command"
        data = {
            **kwargs,
            "name": name,
        }
        res = self.request_post(path, data=data)
        return res

    ## DISKSPACE

    # GET /diskspace
    def get_disk_space(self):
        """Retrieves info about the disk space on the server.

        Args:
            None
        Returns:
            JSON Response (dict)
        """
        path = "/api/diskspace"
        res = self.request_get(path)
        return res

    ## EPISODE

    # GET /episode
    def get_episodes_by_series_id(self, id_):
        """Returns all episodes for the given series

        Args:
            [Required] id_ (int):
        Returns:
            JSON Response (dict)
        """
        path = "/api/episode"
        params = {"seriesId": id_}
        res = self.request_get(path, params=params)
        return res

    # GET /episode/{id}
    def get_episode_by_episode_id(self, id_):
        """Returns the episode with the matching ID.

        Args:
            [Required] id_ (int):
        Returns:
            JSON Response (dict)
        """
        path = f"/api/episode/{id_}"
        res = self.request_get(path)
        return res

    # PUT /episode
    def upd_episode(self, data):
        """Update the given episodes, currently only monitored is changed, all
        other modifications are ignored. All parameters (you should perform a
        GET/{id} and submit the full body with the changes, as other values may
        be editable in the future.

        Args:
            [Required] data (dict) - data payload
        Returns:
            JSON Response (dict)
        """
        path = "/api/episode"
        res = self.request_put(path, data=data)
        return res

    ## EPISODE FILE

    # GET /episodefile
    def get_episode_files_by_series_id(self, id_):
        """Returns all episode files for the given series.

        Args:
            [Required] id_ (int):
        Returns:
            JSON Response (dict)
        """
        path = "/api/episodefile"
        params = {"seriesId": id_}
        res = self.request_get(path, params=params)
        return res

    # GET /episodefile/{id}
    def get_episode_file(self, id_):
        """Returns the episode file with the matching ID.

        Kwargs:
            [Required] id_ (int)
        Returns:
            JSON Response (dict)
        """
        path = f"/api/episodefile/{id_}"
        res = self.request_get(path)
        return res

    # DELETE /episodefile/{id}
    def del_episode_file(self, id_):
        """Delete the given episode file.

        Kwargs:
            [Required] id_ (str)
        Returns:
            JSON Response (dict)
        """
        path = f"/api/episodefile/{id_}"
        res = self.request_del(path)
        return res

    # PUT /episodefile/{id}
    def upd_episode_file_quality(self, id_, data):
        """Updates the quality of the episode file and returns the episode file.

        Kwargs:
            [Required] id_ (str)
            [Required] data (dict) - See Sonarr docs for formatting

        Returns:
            JSON Response (dict)
        """
        path = f"/api/episodefile/{id_}"
        res = self.request_put(path, data=data)
        return res

    ## HISTORY

    # GET /history
    def get_history(self, sort_key, page=1, page_size=10, sort_dir="desc", id_=None):
        """Gets history (grabs/failures/completed)

        Args:
            [Required] sort_key (str) - series.title or date
            [Optional] page (int) - Default: 1
            [Optional] page_size (int) - Default: 10
            [Optional] sort_dir (str) - asc or desc - Default: desc
            [Optional] id_ (int) - Filters to a specific episode ID
        Returns:
            JSON Response (dict)
        """
        path = "/api/history"
        params = {
            "sortKey": sort_key,
            "page": page,
            "pageSize": page_size,
            "sortDir": sort_dir,
        }
        if id_:
            params["episodeId"] = id_
        res = self.request_get(path, params=params)
        return res

    ## WANTED (MISSING)

    # GET /wanted/missing
    def get_wanted(self, sort_key, page=1, page_size=10, sort_dir="asc"):
        """Gets Wanted / Missing episodes

        Args:
            [Required] sort_key (str) - series.title or airDateUtc
            [Optional] page (int) - Default: 1
            [Optional] page_size (int) - Default: 10
            [Optional] sort_dir (str) - asc or desc - Default: asc
        Returns:
            JSON Response (dict)
        """
        path = "/api/wanted/missing"
        params = {
            "sortKey": sort_key,
            "page": page,
            "pageSize": page_size,
            "sortDir": sort_dir,
        }
        res = self.request_get(path, params=params)
        return res

    ## QUEUE

    # GET /queue
    def get_queue(self):
        """Gets current downloading info

        Args:
            None
        Returns:
            JSON Response (dict)
        """
        path = "/api/queue"
        res = self.request_get(path)
        return res

    # DELETE /queue
    def del_queue(self, id_, blacklist=True):
        """Deletes an item from the queue and download client.
        Optionally blacklist item after deletion.

        Args:
            [Required] id_ (int)
            [Optional] blacklist (bool) - Default: True
        Returns:
            JSON Response (dict)
        """
        params = {"id": id_, "blacklist": blacklist}
        path = "/api/queue/"
        res = self.request_del(path, params=params)
        return res

    ## PARSE

    # GET /parse
    def get_parsed_title(self, title):
        """Returns the result of parsing a title.

        Args:
            [Required] title (str)
        Returns:
            JSON Response (dict)
        """
        params = {"title": title}
        path = "/api/parse"
        res = self.request_get(path, params=params)
        return res

    # GET /parse
    def get_parsed_path(self, path):
        """Returns the result of parsing a path.

        Args:
            path (str)
        Returns:
            JSON Response (dict)
        """
        params = {"path": path}
        path_ = "/api/parse"
        res = self.request_get(path_, params=params)
        return res

    ## PROFILE

    # GET /profile
    def get_quality_profiles(self):
        """Gets all quality profiles

        Args:
            None
        Returns:
            JSON Response (dict)
        """
        path = "/api/profile"
        res = self.request_get(path)
        return res

    ## RELEASE

    # GET /release
    def get_releases(self, id_):
        """Get a release with a specific episode ID.

        Args:
            [Required] id_ (str)
        Returns:
            JSON Response (dict)
        """
        params = {"episodeId": id_}
        path = "/api/release"
        res = self.request_get(path, params=params)
        return res

    # POST /release
    def download_release(self, guid, indexer_id):
        """Sends a release with a specific episode ID to the download client.

        Args:
            [Required] guid (str)
            [Required] indexerId (int)
        Returns:
            JSON Response (dict)
        """
        data = {"guid": guid, "indexerId": indexer_id}
        path = "/api/release"
        res = self.request_post(path, data=data)
        return res

    # POST /release/push
    def push_release(self, title, download_url, protocol, publish_date):
        """Notifies Sonarr of a new release.

        Args:
            [Required] title (str) - Release name
            [Required] download_url (str) - .torrent file URL
            [Required] protocol (str) - "Usenet" or "Torrent"
            [Required] publish_date (str) - ISO8601 date string
        Returns:
            JSON Response (dict)
        """
        data = {
            "title": title,
            "downloadUrl": download_url,
            "protocol": protocol,
            "publishDate": publish_date,
        }
        path = "/api/release/push"
        res = self.request_post(path, data=data)
        return res

    ## ROOT FOLDER

    # GET /rootfolder
    def get_root_folder(self):
        """Returns the Root Folder

        Args:
            None
        Returns:
            JSON Response (dict)
        """
        path = "/api/rootfolder"
        res = self.request_get(path)
        return res

    ## SERIES
    # GET /series and /series/{id}
    def get_series(self, id_):
        """Return all series in your collection or the series
        with the matching series ID if one is found.

        Args:
            [Optional] id_
        Returns:
            JSON Response (dict)
        """
        if id_:
            path = f"/api/series/{id_}"
        else:
            path = "/api/series"

        res = self.request_get(path)
        return res

    # POST /series
    def add_series(
        self,
        tvdb_id,
        quality_profile_id,
        root_dir,
        season_folder=True,
        monitored=True,
        ignore_episodes_with_files=False,
        ignore_episodes_without_files=False,
        search_for_missing_episodes=False,
    ):
        """Add a new series to your collection

        Args:
            [Required] tvdb_id (int)
            [Required] qualityProfileId (int)
            [Required] root_dir (str)
            [Optional] season_folder (bool)
            [Optional] monitored (bool)
            [Optional] ignore_episodes_with_files (bool)
            [Optional] ignore_episodes_without_files (bool)
            [Optional] search_for_missing_episodes (bool)
        Returns:
            JSON Response (dict)
        """
        series_json = self.construct_series_json(
            tvdb_id,
            quality_profile_id,
            root_dir,
            season_folder,
            monitored,
            ignore_episodes_with_files,
            ignore_episodes_without_files,
            search_for_missing_episodes,
        )

        path = "/api/series"
        res = self.request_post(path, data=series_json)
        return res

    # PUT /series
    def upd_series(self, data):
        """Update an existing series.

        Args:
            [Required] data (dict) Contains an object obtained by getSeries()
        Returns:
            JSON Response (dict)
        """
        path = "/api/series"
        res = self.request_put(path, data=data)
        return res

    # DELETE /series/{id}
    def del_series(self, id_, delete_files=False):
        """Delete the series with the given ID

        Args:
            [Required] id_ (int)
            [Optional] delete_files (bool) - Default: False
        Returns:
            JSON Response (dict)
        """
        # File deletion does not work
        params = {"deleteFiles": delete_files}
        path = f"/api/series/{id_}"
        res = self.request_del(path, params=params)
        return res

    # GET /series/lookup
    def lookup_series(self, term):
        """Searches for new shows on tvdb

        Args:
            [Required] term (str)
        Returns:
            JSON Response (dict)
        """
        params = {"term": term}
        path = "/api/series/lookup"
        res = self.request_get(path, params=params)
        return res

    # GET /series/lookup
    def lookup_series_by_tvdb_id(self, id_):
        """Searches for new shows on tvdb

        Args:
            [Required] id_ (int) - TVDB ID of a show
        Returns:
            JSON Response (dict)
        """
        params = {"term": f"tvdb:{id_}"}
        path = "/api/series/lookup"
        res = self.request_get(path, params=params)
        return res

    ## SYSTEM

    # GET /system/status
    def get_system_status(self):
        """Returns the System Status as json

        Args:
            None
        Returns:
            JSON Response (dict)
        """
        path = "/api/system/status"
        res = self.request_get(path)
        return res

    # GET /system/backup
    def get_backup(self):
        """Returns the backups as json

        Args:
            None
        Returns:
            JSON Response (dict)
        """
        path = "/api/system/backup"
        res = self.request_get(path)
        return res

    ## TAG

    # GET /tag and /tag/{id}
    def get_tag(self, id_=None):
        """Get all tags in the database, or return a given tag and its label by the database id.

        Args:
            [Optional] id_ (int)
        Returns:
            JSON Response (dict)
        """
        if not id_:
            path = "/api/tag"
        else:
            path = f"/api/tag/{id_}"

        res = self.request_get(path)
        return res

    # POST /tag
    def create_tag(self, id_, label):
        """Create a new tag that can be assigned to a movie, list, delay profile, notification, or restriction.

        Args:
            [Required] id_ (int)
            [Required] label (str)
        Returns:
            JSON Response (dict)
        """
        data = {"id": id_, "label": label}
        path = "/api/tag"
        res = self.request_post(path, data=data)
        return res

    # PUT /tag/{id}
    def upd_tag(self, id_, label):
        """Edit a Tag by its database id.

        Args:
            [Required] id_ (int)
            [Required] label (str)
        Returns:
            JSON Response (dict)
        """
        data = {"id": id_, "label": label}
        path = f"/api/tag/{id_}"
        res = self.request_put(path, data=data)
        return res

    # DELETE /tag/{id}
    def del_tag(self, id_):
        """Delete a tag.

        Args:
            [Required] id_ (int)
        Returns:
            JSON Response (dict)
        """
        path = f"/api/tag/{id_}"
        res = self.request_del(path)
        return res

    ## LOG

    # GET /log
    def get_logs(
        self,
        page=1,
        page_size=10,
        sort_key="time",
        sort_dir="desc",
        filter_key=None,
        filter_value="All",
    ):
        """Gets Sonarr Logs

        Kwargs:
            [Required] None
            [Optional] page (int) - Page number - Default: 1.
            [Optional] page_size (int) - Records per page - Default: 10.
            [Optional] sort_key (str) - What key to sort on - Default: 'time'.
            [Optional] sort_dir (str) - asc or desc - Default: desc.
            [Optional] filter_key (str) - What key to filter - Default: None.
            [Optional] filter_value (str) - Warn, Info, Error - Default: All.
        Returns:
            JSON Response (dict)
        """
        path = "/api/log"
        params = {
            "page": page,
            "pageSize": page_size,
            "sortKey": sort_key,
            "sortDir": sort_dir,
            "filterKey": filter_key,
            "filterValue": filter_value,
        }
        res = self.request_get(path, params=params)
        return res
