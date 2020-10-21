from xbmcvfs import File
import xbmc

class ChasePlayer(xbmc.Player):

    def __init__(self):
        xbmc.Player.__init__(self)
        self.chase_play_event = False
        self.orig_file_size = 0
        self.orig_total_time = 0

    # check for a seek request past the end of the currently playing file.
    # if that file has grown since first starting it, then re-start the video and seek to our requested time
    def onPlayBackSeek(self, time, seek_offset):
        # check if the desired seek is past the end of the currently playing file, and that the file size has grown
        # if so, stop and re-start the file to load the new video duration
        # note: after restarting the video and seeking to the initial time, this function will again be called
        #       hence, check if a chase play event (chase_play_event=True) is currently in progress
        if not self.chase_play_event and self.video_is_file and \
                time >= self.orig_total_time*1000 and \
                self.orig_file_size < self.get_playing_file_size():
            xbmc.log("Chase Player detected in-progress recording.", level=xbmc.LOGNOTICE)
            xbmc.log("time: %s, offset: %s, total_time: %s, orig_size: %s, size: %s" % (time, seek_offset,
                                                                                        self.orig_total_time,
                                                                                        self.orig_file_size,
                                                                                        self.get_playing_file_size()),
                     level=xbmc.LOGNOTICE)
            self.stop()
            self.play(self.video_file_name, windowed=False)
            # flag that a chase play event occurred
            self.chase_play_event = True
            # note: if seek attempt occurs past the original duration of the video
            # seek_offset will reflect the time elapsed since the end of the video. add this to the restart time
            if seek_offset < 0:
                self.restart_seek_time = self.orig_total_time-(seek_offset/1000)
            else:
                self.restart_seek_time = time/1000

    def onAVStarted(self):
        # check if a seek was attempted past the end of an in-progress recording and triggered a restart of the video
        # attempt to resume the previously playing video at the same point
        if self.chase_play_event:
            xbmc.log("Chase Player Seeking to: %s Total: %s" % (self.restart_seek_time, self.getTotalTime()),
                     level=xbmc.LOGNOTICE)

            # if the new seek location is greater than the video's updated duration
            # set the current play time to be close (10s) to the end of the video
            if self.restart_seek_time > self.getTotalTime():
                self.seekTime(self.getTotalTime()-10)
            else:
                self.seekTime(self.restart_seek_time)

        else:
            # check if we're playing a locally accessible video file
            try:
                self.video_file_name = self.getPlayingFile()
            except:
                self.video_is_file = False
            else:
                self.video_is_file = True

        # clear the chase play event flag
        self.chase_play_event = False
        
        # update the video file's size and duration
        if self.video_is_file:
            self.orig_file_size = self.get_playing_file_size()
            self.orig_total_time = self.getTotalTime()

    # @todo seems this API is changing for v19?
    def get_playing_file_size(self):
        f = File(self.video_file_name)
        s = f.size()
        f.close()
        return s
