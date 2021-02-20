from xbmcvfs import File
from xbmcaddon import Addon
import xbmc

class ChasePlayer(xbmc.Player):

    def __init__(self):
        xbmc.Player.__init__(self)
        # Addon object to get addon settings
        self.xbmc_addon = Addon()
        # initialize class vars
        self.chase_play_event = False  # flag that a seek occurred past the video's duration
        self.orig_file_size = 0        # video file size when playback is started
        self.orig_total_time = 0       # video duration when playback is started
        self.video_is_file = False     # video is a locally-accessible file
        self.restart_seek_time = 0     # time to seek

    # check for a seek request past the end of the currently playing file.
    # if that file has grown since first starting it, then re-start the video and seek to our requested time
    def onPlayBackSeek(self, time, seek_offset):
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

            # flag that a chase play event occurred
            self.chase_play_event = True

            # if seek attempt occurs past the original duration of the video
            # seek_offset will reflect the time elapsed since the end of the video. add this to the restart time
            if seek_offset < 0:
                self.restart_seek_time = self.orig_total_time-(seek_offset/1000)
            # restart the video at the previous end point without adding the desired seek time
            elif self.xbmc_addon.getSetting('restart_end_point') == "true" and time > seek_offset:
                self.restart_seek_time = (time-seek_offset)/1000
            else:
                self.restart_seek_time = time/1000

            # stop and re-start the video file
            self.stop()
            self.play(self.video_file_name, windowed=False)

    def onAVStarted(self):
        # check if a seek was attempted past the end of an in-progress recording and triggered a restart of the video
        # attempt to resume the previously playing video at the desired seek location
        if self.chase_play_event:
            xbmc.log("Chase Player Seeking to: %s Total: %s" % (self.restart_seek_time, self.getTotalTime()),
                     level=xbmc.LOGNOTICE)

            # if the new seek location is still greater than the video's updated duration
            # set the current play time to be close to the end of the video
            if self.restart_seek_time > self.getTotalTime():
                # retrieve our buffer setting
                end_buffer = int(self.xbmc_addon.getSetting('end_buffer'))
                self.seekTime(self.getTotalTime()-end_buffer)
            else:
                self.seekTime(self.restart_seek_time)

        else:
            # check if we're playing a locally accessible video file
            try:
                self.video_file_name = self.getPlayingFile()
            except:
                self.video_is_file = False
            else:
                # check that this is a video and not a PVR live-tv URL
                if self.isPlayingVideo() and not self.video_file_name.startswith("pvr"):
                    self.video_is_file = True
                else:
                    self.video_is_file = False

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
